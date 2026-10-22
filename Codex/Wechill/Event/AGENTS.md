# AGENTS.md — Event 目录活动业务

> 父目录 `..\AGENTS.md` 的通用规范（Python 执行路径、MCP 配置、数据库查询规范、输出风格）同样适用于本子目录。

## 活动列表

| 目录 | 说明 |
|------|------|
| `充值活动/` | 充值活动（日/周/月档位 + 榜单） |

---

## 充值活动

### 核心表
`app_act_config` → `app_act_award_config` → `app_act_user_award_record` → `app_act_user_award_record_detail` → `app_act_rank_data`

### 活动状态

查询活动时从目标数据库的 `app_act_config` 读取 `activity_code`、`region`、`begin_time`、`end_time` 和 `status`；活动时间和状态会调整。

### 充值活动区域枚举
- `0` — 英语区 (en)
- `2` — 中东区 (mena)

实际充值流水按 `app_user_flag.region` 归属大区；该字段的 `3` 为土耳其区。充值金额及状态字段见 `充值活动/数据库表结构.md`。

### rank_type 枚举
| rank_type | 含义 |
|-----------|------|
| 1 | 日充值档 |
| 2 | 周充值档 |
| 3 | 月充值档 |
| 11 | 周榜 |
| 12 | 月榜 |

> 每笔充值写入 5 条 rank_data（rank_type = 1, 2, 3, 11, 12），score 相同。统计累计充值时需指定单个 rank_type 再 SUM，避免重复计算。

### 数据库操作规范
- 首次查表先 `SHOW COLUMNS FROM <表名>`（当前 MySQL 版本不支持 `DESC`）。
- 枚举语义从本文件及 `数据库表结构.md` 获取，禁止猜测。
- 查询用户时优先使用 `user_number` 通过 `app_user.user_number` 匹配，仅当明确指定时才用 `user_id`。
- 读取数据后先输出 `列名` 及 `前 3 行` 确认结构。

### 常用操作
- SQL 查询: 使用 `mcp__mysql__mysql_query`
- Redis 查询: 使用 `mcp__redis__read`
- DDL 见 `充值活动/ddl.sql`
- 常用 SQL 见 `充值活动/业务查询.sql`
- Redis key 规范见 `充值活动/redis_keys.md`
- 档位奖励配置见 `充值活动/充值活动档位奖励.md`
