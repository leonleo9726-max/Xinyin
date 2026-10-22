# AGENTS.md — Top 项目规则

本文件是 `Top/` 项目默认规则入口；子目录如有 `AGENTS.md`，以子目录规则为准。

## 1. 项目边界

- 当前项目根目录：`E:\Codex\Top`；处理项目文件前先确认位于该目录或其子目录。
- `Top/` 与同级 `Wechill/` 相互独立；严禁读取、搜索、引用 `Wechill/`。
- 仅当用户明确点名 `Wechill/` 并要求对比、迁移或同步时，才允许读取用户指定范围。

## 2. 环境执行

- Python 固定使用：`E:\python\work\.venv\Scripts\python.exe`。
- Python 必须写入 `.py` 文件后执行，禁止 `python -c`、管道内联脚本。
- Shell 使用 Windows PowerShell / Git Bash。
- 用户明确要求与项目默认规则冲突时，先说明冲突及影响，并等待用户在后续消息中明确二次授权后再执行；授权仅适用于确认的具体操作。不得因此绕过更高优先级指令或不可覆盖的权限、安全约束。
- 遇到路径、编码、逻辑异常时先自查修正，只向用户展示必要结论和关键异常。
- 每次拉取 `code\` 下任一仓库的最新代码后，必须按 `code\AGENTS.md` 的“同步后文档审查”完成规则与架构复核，再结束拉取任务。

## 3. 配置

- 本地服务配置写入 `.env`，敏感信息不得提交；模板写入 `.env.example`。
- 新增外部服务、账号、密钥、回调地址时，同步更新 `.env` 与 `.env.example`。
- 项目级 MCP 配置写入 `.codex/config.toml`，使用 `[mcp_servers.<name>]`。

## 4. 数据库查询

- 默认查询或变更数据前先确认是测试环境。经明确授权的生产薪资只读查询，仅可通过
  `guild-salary-query` 的 `--environment production --confirm-production` 分支执行；生产写操作仍禁止。
- 首次查询表前必须执行 `SHOW COLUMNS FROM <表名>`；当前 MySQL 不使用 `DESC`。
- 用户输入的纯数字默认视为 `user_no`，通过 `ln_user.user_no` 获取 `user_id`；仅当用户明确说明“这是 `user_id`”时才按 `user_id` 查询。
- 查询用户相关表时按业务用户号字段查询：`ln_user` 用 `user_no`，其他用户表优先用 `user_number`，禁止误用自增 `id` 当用户号。
- 判断“用户不存在”前，需同时检查主用户表及相关扩展/审核用户表。
- 表或字段报错时，先对照 `数据库表结构.md` 校验；发现新字段、枚举、表关系后立即更新该文档。
- 单个任务需要 3 次及以上连续 MySQL 查询时，必须写 Python 脚本用 `mysql connector` 一次完成，禁止逐条手动调用 MCP MySQL。

## 5. Redis / RabbitMQ

- 查询 Redis 前确认 DB 编号、key 前缀、过期策略。
- Redis 操作先依次查询 DB7（默认库）和 DB10（主要库），确认目标 key 所在逻辑库后才能读取、清理或变更；两个库均未命中或同时命中时，先声明结果并等待确认。
- 查询 RabbitMQ 前确认 vhost、exchange、queue、routing key。
- 发现新的 key、队列、路由规范后，补充到项目文档或对应子目录规则。

## 6. 数据质量

- 读取结构化数据后先确认列名和前 3 行。
- 发现空值、非法格式、重复主键、数据偏移、异常状态时，结论前单独列出「**异常声明**」。
- 跨系统核验时说明数据源和时间范围。

## 7. 输出

- 使用简体中文，结论先行，极简专业。
- 禁用“好的”“我明白了”等社交填充。
- 多维数据用 Markdown 表格；核心结论/关键数值加粗；文件名、路径、变量名用反引号。
- 账号、密码、token、连接串默认脱敏。

## 8. MCP 排障

- 先确认当前目录在 `E:\Codex\Top` 或其子目录。
- 用 `codex mcp list` 验证 `mysql`、`redis`、`rabbitmq` 是否加载；TUI 内用 `/mcp` 验证。
- 不要把 Top 服务复制到 `E:\Codex\.mcp.json` 或 `Wechill/`。
- 配置变更后需完全重启 Codex。
