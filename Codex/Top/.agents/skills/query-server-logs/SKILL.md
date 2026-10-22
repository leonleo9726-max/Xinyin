---
name: query-server-logs
description: Query Top project room-api or app-api HTTP request logs over the configured SSH connection. Use when the user asks to inspect recent server requests by business user number, internal user ID, service, or time range.
---

# Query Server Logs

Use the bundled script for request-log queries. It maps business user numbers through
`ln_user`, filters on the server, and emits JSON.

## Run

Use the project Python executable from any directory:

```powershell
& 'E:\python\work\.venv\Scripts\python.exe' '<skill-dir>\scripts\query_logs.py' room-api --user-no 6729461 --limit 10
```

- Select `room-api` or `app-api` from the user's request.
- Treat a plain number as `user_no`; pass `--user-no`.
- Pass `--user-id` only when the user explicitly identifies the number as the internal database `user_id`.
- Default to 10 requests and the `.env` `APP_ENV`. Use `--environment test|production` when the user specifies an environment.
- Add `--since` or `--until` for an ISO-8601 local timestamp. Increase `--log-files` only when the requested range predates the default four newest logs.
- Add `--include-response` when the user asks for response information. It returns a redacted compact summary containing the business code, message, key scalar fields, collection counts, and original body length.

Run `--help` when the requested options are unclear. Do not recreate SSH or parsing logic in an ad hoc script.

## Report

Render `requests` as a concise Markdown table containing time, method, URI, request body,
status, duration, response summary when requested, and request ID. State the data source,
environment, timezone from the log timestamps, and covered time range. Highlight non-2xx
responses, non-success business codes, and unusually slow requests.

The script omits response bodies by default. With `--include-response`, it summarizes them
after redacting common credential and contact fields. Do not expose `.env` values or
connection details. An empty request list means no matching request was found in the scanned
files; it does not prove the user does not exist.

The query is complete when the command succeeds, the environment and resolved ID are clear,
and every returned request is represented in the result.
