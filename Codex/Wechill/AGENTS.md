# AGENTS.md — 项目根规范

子目录各有独立 `AGENTS.md`（见 §2），本文件为全局默认；冲突时以子目录为准。

> Codex 迁移后以 `AGENTS.md` 为唯一项目规则入口。

## 0. 项目边界 (Project Boundary)

- `Wechill/` 是独立项目，严禁读取、搜索、引用同级 `Top/` 项目中的任何文件。
- 仅当用户明确点名 `Top/` 并要求跨项目对比、迁移或同步时，才允许读取用户点名范围内的 `Top/` 文件。
- 不得用 `Top/` 的规则、数据、脚本或输出作为 Wechill 任务依据。

## 1. 环境与执行 (Environment)

- **PYTHON_EXE**: `E:\python\work\.venv\Scripts\python.exe`
- **SHELL**: Windows PowerShell / Git Bash
- **Python 执行约束**:
  - 必须使用 `${PYTHON_EXE}` 全路径调用。
  - 必须将脚本写入 `.py` 文件后执行 —— **禁止** `python -c` 内联或将 Python 管道到 Bash（Windows Store Python 桩与 Git Bash 冲突，exit code 49）。
  - 脚本仅用 ASCII 字符，终端 GBK 编码遇中文/Unicode/emoji 会崩。
- **自我修复**: 遇路径、编码、逻辑异常自动分析并修正重试，忽略非必要中间过程，直接展示最终结论。

## 2. 项目地图 (Project Map)

| 目录 | 用途 | 子 AGENTS.md |
|------|------|:---:|
| `Payroll/` | 多地区主播/公会长薪资计算（双周/自由，英语区/中东区） | ✅ |
| `BDM/` | BD/BDM 薪资计算与公会管理 | ✅ |
| `Event/` | 活动管理 | ✅ |
| `PRD/` | 产品需求文档 | ✅ |
| `code/` | 26 个云效代码仓库；拉取、构建和架构规则见 `code/AGENTS.md` 与 `code/ARCHITECTURE.md` | ✅ |

- 操作前先确认当前在正确子目录，再查询数据库或读取文件。
- 探索项目时先与用户确认目标目录，不无差别扫描不相关文件夹。
- 拉取或更新 `code/` 下仓库后，完成 `code/AGENTS.md` 的“同步后文档审查”，再报告任务完成。

## 3. 数据库查询规范 (Database Conventions)

- **默认数据源**: 除非用户明确要求查询生产库，否则一律使用测试库 MCP `mysql`（`stay` 库）。`mysql_prod` 仅限用户明确指定“生产库”时使用。
- **用户 ID 默认语义**: 用户输入的数字默认视为 `user_number`，通过 `app_user.user_number` 匹配获取 `user_id`。仅当用户明确说明"这是 user_id"时直接按 `user_id` 查询。
- **查询所有用户表时一律用 `user_number`**（`app_user_agency`、薪资记录等均适用），禁止直接用 `id`。
- **首次查表先 `SHOW COLUMNS FROM <表名>`**（当前 MySQL 版本不支持 `DESC`）。
- **用户查找**: 同时检查主用户表及扩展/审核用户表，再得出"用户不存在"的结论。
- **Schema 维护**: 发现新字段映射、枚举值、表关系后，立即更新 `数据库表结构.md`（BDM 子项目位于 `BDM/rules/`，Payroll 位于其子目录下）。


## 4. 数据质量门禁 (Data Quality Gate)

- **预览先行**: 读取数据后先输出 `列名` 及 `前 3 行` 确认结构。
- **质量巡检**: 发现空值 (NaN)、格式非法、数据偏移时，在结论前以「**异常声明**」单独列出，严禁忽略。

## 5. 输出风格 (Output Style)

- **语言**: 简体中文。结论先行，极简专业。禁用"好的"、"我明白了"等社交填充词。
- **格式**:
  - 数据对比/多维数据 → **Markdown 表格**
  - 核心结论/数值/关键变动 → **加粗**
  - 文件名/路径/变量名 → `反引号`
- **薪资/佣金结果**: 必须展示**完整**表格，禁止截断。结果长时用 Markdown 表格确保所有行完整呈现。
- **测试用例**: Format B 层次化清单 —— 编号模块 + `- X.Y.Z 描述`，不使用 `- [ ]` 复选框。

## 6. 领域规则 (Domain Rules)

### 6.1 Payroll 关键字段

- **gain_coin**: 公会长档位判定 + 分成计算
- **gain_diamond**: 主播档位判定 + 佣金率计算
- **严禁互替**，每次计算前重新查询数据库取最新值，不复用缓存。

### 6.2 业务规则格式

提取或精炼业务规则时使用结构化格式，包含以下字段：

- **Rule Name** | **Trigger Condition** | **Formula** | **Threshold Values** | **Applicable Policy**

紧凑、可扫描，目标 AGENTS.md 密度，非文档式展开。

### 6.3 薪资计算入口

- 主播/公会长薪资 → 先加载 `Payroll/核心业务规则.md`，再查用户数据。
- BD/BDM 薪资 → 先加载 `BDM/rules/BDM业务规则.md`，走 Payroll 底层链路交叉验证。

## 7. MCP 排障

MCP 服务器（mysql/redis）在 `/mcp` 不显示时：
1. 确认当前目录位于 `E:\Codex\Wechill` 或其子目录，并使用项目级 `E:\Codex\Wechill\.codex\config.toml`。
2. Codex 官方项目级 MCP 配置使用 `[mcp_servers.<name>]` 表；不要把 Wechill 服务复制到 `E:\Codex\.mcp.json` 或 `Top/`。
3. 运行 `codex mcp list` 验证应显示 `mysql`、`mysql_prod`、`redis`；TUI 内用 `/mcp` 验证。
4. 验证 `npx` 包和本地启动脚本存在；配置变更后需完全重启 Codex。
