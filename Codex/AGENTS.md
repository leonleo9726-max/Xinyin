# AGENTS.md — Codex 工作区顶层

- `E:\Codex` 为工作区/Git 顶层，不代表单一业务项目。
- `Wechill/` 与 `Top/` 是两个并列、相互独立的项目；处理项目文件前先进入目标项目目录。
- **严禁跨项目读取**：进入 `Wechill/` 后不得读取、搜索、引用 `Top/`；进入 `Top/` 后不得读取、搜索、引用 `Wechill/`。
- 只有当用户在同一条请求中明确点名两个项目并要求对比、迁移或同步时，才允许跨项目读取；读取范围必须限于用户点名的文件或目录。
- 用户未明确目标项目时，先询问目标项目，不得为了判断意图同时扫描两个项目。
- 进入 `Wechill/` 后读取 `Wechill/AGENTS.md` 及更深层子目录 `AGENTS.md`；Wechill 的业务规则不适用于 `Top/`。
- 进入 `Top/` 后读取 `Top/AGENTS.md`；Top 的项目规则在该目录内维护。
- MCP 配置按 Codex 官方项目级方式写入项目内 `.codex/config.toml`，使用 `[mcp_servers.<name>]` 表；进入 `Top/` 或 `Wechill/` 后用 `codex mcp list` / `/mcp` 验证当前项目加载的服务。
- 旧式 `.mcp.json` 仅作为本机迁移参考，不作为 Codex 官方项目级配置入口；只有明确为工作区共享服务时，才考虑工作区级配置，且不得覆盖项目专属 MCP。
- 工作区级本地工具放在 `tools/`；PowerShell profile 通过该目录加载本地 `rg`。
