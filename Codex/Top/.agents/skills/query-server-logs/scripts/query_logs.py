"""Query recent Top HTTP request logs with optional response summaries."""

from __future__ import annotations

import argparse
from datetime import date, datetime
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import sys
from typing import Any

import mysql.connector
import paramiko


LOG_NAME_PATTERN = re.compile(r"^info(?:\.(\d{4}-\d{2}-\d{2}))?\.log$")
TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})?$"
)
REQUEST_PATTERN = re.compile(
    r"^(?P<time>\S+) .*RequestResponseLoggingFilter : http body "
    r"id=(?P<request_id>\S+) method=(?P<method>\S+) uri=(?P<uri>\S+) "
    r"status=(?P<status>\d+) cost_ms=(?P<cost_ms>\d+) "
    r"user_id=(?P<user_id>\d+) request_body=(?P<request_body>.*?)"
    r"(?: response_body=(?P<response_body>.*))?$"
)
SERVICE_LOG_SETTING = {
    "room-api": "LOG_ROOM_API_DIR",
    "app-api": "LOG_APP_API_DIR",
}
SENSITIVE_PATTERNS = (
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,}\]]+"), r"\1***"),
    (
        re.compile(
            r"(?i)([\"']?(?:access_?token|refresh_?token|token|password|passwd)"
            r"[\"']?\s*[:=]\s*[\"']?)[^\s,\"'}\]]+"
        ),
        r"\1***",
    ),
    (re.compile(r"(?i)(email\s*[:=]\s*)[^\s,}\]]+"), r"\1***"),
    (re.compile(r"(?i)((?:phone|mobile)\s*[:=]\s*[\"']?)\+?\d{7,15}"), r"\1***"),
)
SENSITIVE_JSON_KEY = re.compile(
    r"(?i)^(?:authorization|access_?token|refresh_?token|token|password|passwd|email|phone|mobile)$"
)


def find_project_root() -> Path:
    """Find the Top root without depending on the caller's working directory."""
    candidates = (Path.cwd(), *Path(__file__).resolve().parents)
    for candidate in candidates:
        if (candidate / ".env").is_file() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise RuntimeError("Top project root containing .env and AGENTS.md was not found")


def load_env(path: Path) -> dict[str, str]:
    """Read a simple dotenv file without modifying process-wide environment state."""
    settings: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings


def require_setting(settings: dict[str, str], name: str) -> str:
    """Return a required setting without including its value in errors."""
    value = settings.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required .env setting: {name}")
    return value


def normalize_environment(requested: str | None, settings: dict[str, str]) -> str:
    """Resolve the database environment used for user-number mapping."""
    value = (requested or settings.get("APP_ENV") or "test").strip().lower()
    aliases = {"test": "test", "dev": "test", "development": "test", "prod": "production", "production": "production"}
    if value not in aliases:
        raise RuntimeError("Environment must be test or production")
    return aliases[value]


def database_settings(settings: dict[str, str], environment: str) -> dict[str, Any]:
    """Build mysql-connector settings for the selected read-only lookup."""
    prefix = "PROD_MYSQL_" if environment == "production" else "MYSQL_"
    return {
        "host": require_setting(settings, f"{prefix}HOST"),
        "port": int(require_setting(settings, f"{prefix}PORT")),
        "user": require_setting(settings, f"{prefix}USER"),
        "password": require_setting(settings, f"{prefix}PASSWORD"),
        "database": require_setting(settings, f"{prefix}DATABASE"),
        "connection_timeout": 15,
    }


def resolve_user_id(settings: dict[str, str], environment: str, user_no: str) -> str:
    """Resolve a business user number after verifying the live table columns."""
    connection = mysql.connector.connect(**database_settings(settings, environment))
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW COLUMNS FROM ln_user")
        fields = {str(row[0]) for row in cursor.fetchall()}
        required_fields = {"user_id", "user_no"}
        if not required_fields.issubset(fields):
            raise RuntimeError("ln_user does not contain the required user_id and user_no fields")
        cursor.execute(
            "SELECT user_id, user_no FROM ln_user WHERE user_no = %s LIMIT 2",
            (user_no,),
        )
        rows = cursor.fetchall()
    finally:
        connection.close()
    if not rows:
        raise RuntimeError(
            "user_no was not found in ln_user; this does not prove the account does not exist"
        )
    if len(rows) > 1:
        raise RuntimeError("user_no maps to multiple ln_user rows")
    return str(rows[0][0])


def validate_timestamp(value: str | None, option: str) -> str | None:
    """Validate a log-compatible ISO-8601 timestamp."""
    if value is None:
        return None
    if not TIMESTAMP_PATTERN.fullmatch(value):
        raise RuntimeError(f"{option} must be an ISO-8601 local timestamp")
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def redact(value: str) -> str:
    """Mask common credentials and contact fields in log text."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def sanitize_json(value: Any) -> Any:
    """Redact sensitive JSON values by key while preserving useful structure."""
    if isinstance(value, dict):
        return {
            key: "***" if SENSITIVE_JSON_KEY.fullmatch(str(key)) else sanitize_json(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    if isinstance(value, str):
        return redact(value)
    return value


def summarize_data(value: Any, depth: int = 0) -> Any:
    """Keep scalar response facts and replace large collections with counts."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        summary: dict[str, Any] = {"count": len(value)}
        if depth == 0 and len(value) <= 3:
            summary["items"] = [summarize_data(item, depth + 1) for item in value]
        return summary
    if isinstance(value, dict):
        summary = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= 24:
                summary["remaining_field_count"] = len(value) - index
                break
            if isinstance(item, list):
                summary[f"{key}_count"] = len(item)
            elif isinstance(item, dict):
                if depth < 1:
                    summary[key] = summarize_data(item, depth + 1)
                else:
                    summary[f"{key}_field_count"] = len(item)
            else:
                summary[key] = item
        return summary
    return str(value)


def summarize_response(response_body: str) -> dict[str, Any]:
    """Decode a response body into a compact, redacted business summary."""
    sanitized_text = redact(response_body)
    try:
        decoded = sanitize_json(json.loads(sanitized_text))
    except json.JSONDecodeError:
        return {
            "text": sanitized_text[:500],
            "truncated": len(sanitized_text) > 500,
            "body_length": len(response_body),
        }

    if not isinstance(decoded, dict):
        return {
            "data": summarize_data(decoded),
            "body_length": len(response_body),
        }

    summary: dict[str, Any] = {"body_length": len(response_body)}
    if "code" in decoded:
        summary["code"] = decoded["code"]
    message = decoded.get("msg", decoded.get("message"))
    if message is not None:
        summary["message"] = message
    if "data" in decoded:
        summary["data"] = summarize_data(decoded["data"])
    for key, value in decoded.items():
        if key not in {"code", "msg", "message", "data"} and not isinstance(value, (dict, list)):
            summary[key] = value
    return summary


def choose_log_files(
    sftp: paramiko.SFTPClient,
    log_dir: str,
    maximum: int,
    since: str | None,
    until: str | None,
) -> list[str]:
    """Select the newest relevant application logs in chronological order."""
    since_date = date.fromisoformat(since[:10]) if since else None
    until_date = date.fromisoformat(until[:10]) if until else None
    entries = []
    for entry in sftp.listdir_attr(log_dir):
        match = LOG_NAME_PATTERN.fullmatch(entry.filename)
        if not match or not stat.S_ISREG(entry.st_mode):
            continue
        rotated_date = date.fromisoformat(match.group(1)) if match.group(1) else None
        if rotated_date and since_date and rotated_date < since_date:
            continue
        if rotated_date and until_date and rotated_date > until_date:
            continue
        entries.append(entry)
    entries.sort(key=lambda entry: entry.st_mtime)
    return [
        str(PurePosixPath(log_dir) / entry.filename)
        for entry in entries[-maximum:]
    ]


def remote_query_command(
    files: list[str],
    user_id: str,
    limit: int,
    since: str | None,
    until: str | None,
    include_response: bool,
) -> str:
    """Build a read-only command with an optional response body."""
    quoted_files = " ".join(shlex.quote(path) for path in files)
    command = (
        f"grep -hF -- {shlex.quote(f'user_id={user_id} request_body=')} "
        f"{quoted_files}"
    )
    if since or until:
        command += (
            f" | awk -v since={shlex.quote(since or '')} -v until={shlex.quote(until or '')} "
            "'((since == \"\" || $1 >= since) && (until == \"\" || $1 <= until))'"
        )
    command += f" | tail -n {limit}"
    if not include_response:
        command += " | sed 's/ response_body=.*$//'"
    return command


def query_requests(
    client: paramiko.SSHClient,
    files: list[str],
    user_id: str,
    limit: int,
    since: str | None,
    until: str | None,
    include_response: bool,
) -> list[dict[str, Any]]:
    """Execute the remote filter and parse compact request records."""
    command = remote_query_command(files, user_id, limit, since, until, include_response)
    _, stdout, stderr = client.exec_command(command, timeout=45)
    output = stdout.read().decode("utf-8", errors="replace")
    error = stderr.read().decode("utf-8", errors="replace").strip()
    status_code = stdout.channel.recv_exit_status()
    if status_code not in (0, 1):
        raise RuntimeError(f"Remote log query failed: {redact(error) or f'exit {status_code}'}")

    requests = []
    for line in output.splitlines():
        match = REQUEST_PATTERN.match(line)
        if not match:
            continue
        record: dict[str, Any] = match.groupdict()
        record["status"] = int(record["status"])
        record["cost_ms"] = int(record["cost_ms"])
        record["request_body"] = redact(record["request_body"])
        response_body = record.pop("response_body")
        if include_response and response_body is not None:
            record["response"] = summarize_response(response_body)
        requests.append(record)
    return requests


def build_parser() -> argparse.ArgumentParser:
    """Define the stable command-line interface used by the skill."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("service", choices=sorted(SERVICE_LOG_SETTING))
    identity = parser.add_mutually_exclusive_group(required=True)
    identity.add_argument("--user-no", help="Business user number; resolved through ln_user")
    identity.add_argument("--user-id", help="Explicit internal database user_id")
    parser.add_argument("--environment", choices=("test", "production"))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--since", help="Inclusive ISO-8601 local timestamp")
    parser.add_argument("--until", help="Inclusive ISO-8601 local timestamp")
    parser.add_argument("--log-files", type=int, default=4)
    parser.add_argument(
        "--include-response",
        action="store_true",
        help="Include a redacted compact response summary",
    )
    return parser


def main() -> int:
    """Resolve identity, query remote logs, and print one JSON result."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args()
    if args.limit < 1 or args.limit > 100:
        raise RuntimeError("limit must be between 1 and 100")
    if args.log_files < 1 or args.log_files > 31:
        raise RuntimeError("log-files must be between 1 and 31")
    if args.user_no and not args.user_no.isdigit():
        raise RuntimeError("user-no must be numeric")
    if args.user_id and not args.user_id.isdigit():
        raise RuntimeError("user-id must be numeric")

    since = validate_timestamp(args.since, "since")
    until = validate_timestamp(args.until, "until")
    if since and until and since > until:
        raise RuntimeError("since must not be later than until")

    root = find_project_root()
    settings = load_env(root / ".env")
    environment = normalize_environment(args.environment, settings)
    user_id = args.user_id or resolve_user_id(settings, environment, args.user_no)
    log_dir = require_setting(settings, SERVICE_LOG_SETTING[args.service])

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    try:
        client.connect(
            hostname=require_setting(settings, "LOG_SERVER_HOST"),
            port=int(require_setting(settings, "LOG_SERVER_PORT")),
            username=require_setting(settings, "LOG_SERVER_USER"),
            password=require_setting(settings, "LOG_SERVER_PASSWORD"),
            look_for_keys=False,
            allow_agent=False,
            timeout=15,
            auth_timeout=15,
            banner_timeout=15,
        )
        with client.open_sftp() as sftp:
            files = choose_log_files(sftp, log_dir, args.log_files, since, until)
        if not files:
            raise RuntimeError("No matching info log files were found")
        requests = query_requests(
            client,
            files,
            user_id,
            args.limit,
            since,
            until,
            args.include_response,
        )
    finally:
        client.close()

    result = {
        "service": args.service,
        "environment": environment,
        "identity": {
            "user_no": args.user_no,
            "user_id": user_id,
        },
        "files_scanned": len(files),
        "since": since,
        "until": until,
        "response_included": args.include_response,
        "request_count": len(requests),
        "requests": requests,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": redact(str(exc))}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
