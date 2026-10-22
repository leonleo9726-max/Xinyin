-- ============================================================
-- 充值活动 - 常用业务查询
-- ============================================================

-- ▸ 查询所有在生效的活动
SELECT activity_code, activity_name, region, begin_time, end_time, status
FROM app_act_config
WHERE status = 1 AND NOW() BETWEEN begin_time AND end_time;

-- ▸ 查询某活动的奖励配置（按档位）
SELECT tier, prize_type, prize_id, amount, distribute_type, remark
FROM app_act_award_config
WHERE activity_code = 'recharge_en' AND status = 1
ORDER BY tier ASC;

-- ▸ 查询用户累计充值（按 rank_type=1 日充值档，避免重复计算）
SELECT user_id, SUM(score) AS total_recharge
FROM app_act_rank_data
WHERE activity_code = 'recharge_en' AND rank_type = 1
GROUP BY user_id
ORDER BY total_recharge DESC
LIMIT 20;

-- ▸ 查询用户各维度充值档位
SELECT user_id,
  MAX(CASE WHEN rank_type = 1 THEN score END) AS day_tier,
  MAX(CASE WHEN rank_type = 2 THEN score END) AS week_tier,
  MAX(CASE WHEN rank_type = 3 THEN score END) AS month_tier
FROM app_act_rank_data
WHERE activity_code = 'recharge_en' AND user_id = ?
GROUP BY user_id;

-- ▸ 查询用户每笔充值明细（按 create_time 聚合 5 个 rank_type 为一笔）
SELECT user_id, score, create_time, COUNT(*) AS type_count
FROM app_act_rank_data
WHERE activity_code = 'recharge_en' AND user_id = ?
GROUP BY user_id, score, create_time
ORDER BY create_time DESC;

-- ▸ 查询用户已领取的奖励
SELECT user_id, award_type, tier, award_date, receive_status
FROM app_act_user_award_record
WHERE activity_code = 'recharge_en' AND user_id = ?;

-- ▸ 查询某天发放的奖励明细
SELECT d.user_id, d.award_type, d.tier, d.prize_id, d.amount, d.receive_status
FROM app_act_user_award_record_detail d
WHERE d.activity_code = 'recharge_en' AND d.award_date = '2026-05-14';

-- ▸ 查询榜单 Top N
SELECT user_id, score
FROM app_act_rank_data
WHERE activity_code = 'recharge_en' AND rank_type = 1
ORDER BY score DESC
LIMIT 10;
