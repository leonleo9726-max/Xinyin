# 充值活动 Redis Key 规范

## 1. 充值榜单 (ZSET)
```
recharge:rank:{period}:{YYYYMMDD}:region:{en|mena}
```
| 参数 | 说明 |
|------|------|
| period | `week` / `month` |
| YYYYMMDD | 周期起始日期（周=周一，月=1号） |
| region | `en`(英语区) / `mena`(中东区) |

示例: `recharge:rank:week:20260518:region:en`

## 2. 用户奖励类型标识 (HASH)
```
payer:recharge:rewards:type:flag:{user_id}
```

## 3. 每日促销标识
```
payer:recharge:today:promotion:flag:{user_id}
```

## 4. 钻石兑换金币
```
payer:recharge:diamond:exchange:gold:coin:user:{YYYYMMDD}:{user_id}
payer:recharge:diamond:exchange:gold:coin:all:{YYYYMMDD}
```

## 5. 准备令牌 (STRING)
```
payer:recharge:prepare:token::{YYYYMMDD}
```

## 6. 活动中心 (STRING)
```
act:center:new:{user_id}
```
