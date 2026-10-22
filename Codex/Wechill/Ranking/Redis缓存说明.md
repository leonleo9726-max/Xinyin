# Redis 缓存说明

## 首页排序相关缓存

| 缓存键前缀 | 已确认键模式/类型 | 业务含义 | 首页排序关联 |
|---|---|---|---|
| `live:room:consume:week` | `live:room:consume:week:{yyyyMMdd}:{room_id}`，String | 近 7 天流水 | 首页排序相关指标 |
| `live:room:consume:today` | `live:room:consume:today:{yyyyMMdd}:{room_id}`，String | 当天流水 | 首页排序相关指标 |
| `live:join:room:member` | `live:join:room:member:{live_id}` | 房间在线人数 | 首页排序相关指标 |
| `live:site-cache` | `live:site-cache:{live_id}` | 在麦人数 | 首页排序相关指标 |
| `live:live:list` | 待确认 | 直播列表 | 首页排序相关缓存 |
| `live:live:detail` | 待确认 | 直播详情 | 首页排序相关缓存 |
| `live:room:top-new` | `live:room:top-new:{yyyyMMdd}:{category_id}`，Hash | 房间置顶缓存 | 首页排序相关缓存 |

> 上述键均涉及首页排序；具体排序权重、刷新周期、在线/在麦缓存值结构和失效策略尚未确认。
