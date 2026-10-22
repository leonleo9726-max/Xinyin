# Ranking 目录规范

## 范围

本目录用于排查首页房间排序输入：房间流水、在线人数、在麦人数和房间置顶 Redis 缓存。

## 数据源

- 默认使用 `mysql` MCP 测试库；只有用户明确要求生产库时才使用 `mysql_prod`。
- Redis 查询使用 `redis` MCP，排序排查仅执行读操作。
- 用户输入数字默认按 `app_user.user_number` 处理；用户明确说明是 `user_id` 时才直接使用。

## 房间排序查询

用户请求房间排序数据时，按以下顺序完成。每个 MySQL 表首次查询前先执行
`SHOW COLUMNS FROM <表名>`。

1. 按 `user_number` 查询 `app_user`，保留 `user_id`、昵称和状态；结论为用户不存在前，同时检查扩展/审核用户表。
2. 按已解析的 `user_id` 查询 `app_live_room`，保留 `room_id`、`live_id`、`room_number`、`category_id`、房间状态和更新时间。
3. 按 `user_id` 或 `room_id` 查询 `app_live`，使用最新记录确认当前 `live_id`、心跳时间和分类。
4. 以北京时间当天生成 `{yyyyMMdd}`，查询下方对应的精确 Redis 键。
5. 键不存在时按缓存未命中输出；需排查同前缀键时，循环执行 `SCAN ... MATCH <prefix>* COUNT 10000` 直至游标为 `0`，不使用 `KEYS`。

## Redis 键映射

| 指标 | 键模式 | 预期类型 | 标识符 |
|---|---|---|---|
| 近七天流水 | `live:room:consume:week:{yyyyMMdd}:{room_id}` | String | `room_id` |
| 当天流水 | `live:room:consume:today:{yyyyMMdd}:{room_id}` | String | `room_id` |
| 房间在线人数 | `live:join:room:member:{live_id}` | 运行时确认 | `live_id` |
| 在麦人数 | `live:site-cache:{live_id}` | 运行时确认 | `live_id` |
| 房间置顶 | `live:room:top-new:{yyyyMMdd}:{category_id}` | Hash | `category_id` |

流水键使用 `GET`。在线和在麦键先使用 `TYPE`，再按实际类型读取。置顶 Hash 使用
`HGETALL`，并明确检查目标 `room_id` 是否出现在字段或值中。

## 输出门禁

- 每份 MySQL 查询结果先展示列名及最多前三行，再得出结论。
- 最终用完整 Markdown 表格展示：指标、来源键或表、结果/状态。
- 将缺失键、空标识符、过期心跳、格式非法值和 Redis 类型不匹配独立列在 **异常声明**。
- 输出已解析的 `user_number`、`user_id`、`room_id`、`live_id` 和查询日期，确保缓存标识可审计。

## 已知约束

Redis 排序键为临时缓存。在线、在麦或置顶键未命中时，表示查询时刻无法从该缓存取得值；不得将未命中推断为人数为零。
