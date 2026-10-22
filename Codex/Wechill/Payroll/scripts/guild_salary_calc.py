"""
Guild Salary Calculation - 2026-06-01 to 2026-06-15
Grouped by guild: member salary, guild summary, guild surplus
"""
from decimal import Decimal, ROUND_DOWN
import json

def floor2(d):
    return d.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

# ============================================================
# TIER CONFIGS (from DB query)
# ============================================================
# (policy, region) -> list of tiers sorted by level ASC
TIERS = {}

# Bi-weekly English (policy=1, region=0)
TIERS[(1, 0)] = [
    (10000, '0.40', '0.00', '0.00', '0.00', 25000),
    (30000, '1.30', '1.00', '0.00', '0.00', 25000),
    (50000, '2.20', '1.00', '0.00', '0.00', 25000),
    (80000, '3.60', '1.00', '0.00', '0.00', 25000),
    (110000, '4.90', '2.00', '0.00', '0.00', 25000),
    (140000, '6.30', '2.00', '0.00', '0.00', 25000),
    (190000, '8.50', '3.00', '0.00', '0.00', 25000),
    (250000, '11.20', '4.00', '0.00', '0.00', 25000),
    (350000, '15.60', '6.00', '0.00', '0.00', 25000),
    (450000, '20.10', '8.00', '0.00', '0.00', 25000),
    (500000, '22.30', '9.00', '0.00', '0.00', 25000),
    (700000, '31.30', '10.00', '5.00', '0.00', 25000),
    (1000000, '44.60', '14.00', '8.00', '0.00', 25000),
    (1500000, '67.00', '22.00', '10.00', '0.00', 25000),
    (2000000, '89.30', '30.00', '10.00', '0.00', 25000),
    (3000000, '133.90', '48.00', '10.00', '0.00', 25000),
    (4000000, '178.60', '61.00', '20.00', '0.00', 25000),
    (5000000, '223.20', '78.00', '20.00', '0.00', 25000),
    (6000000, '267.90', '96.00', '20.00', '0.00', 25000),
    (7000000, '312.50', '114.00', '20.00', '0.00', 25000),
    (8500000, '379.50', '140.00', '20.00', '0.00', 25000),
    (10500000, '468.80', '176.00', '20.00', '0.00', 25000),
    (11500000, '513.40', '188.00', '30.00', '0.00', 25000),
    (14000000, '625.00', '233.00', '30.00', '0.00', 25000),
    (17000000, '758.90', '286.00', '30.00', '0.00', 25000),
    (22000000, '982.10', '374.00', '30.00', '0.00', 25000),
    (27000000, '1205.40', '452.00', '50.00', '0.00', 25000),
    (35000000, '1562.50', '594.00', '50.00', '0.00', 25000),
    (45000000, '2008.90', '771.00', '50.00', '0.00', 25000),
    (60000000, '2678.60', '1036.00', '50.00', '0.00', 25000),
    (70000000, '3125.00', '1213.00', '50.00', '0.00', 25000),
    (90000000, '4017.90', '1541.00', '100.00', '0.00', 25000),
    (120000000, '5357.10', '2071.00', '100.00', '0.00', 25000),
    (150000000, '6696.40', '2602.00', '100.00', '0.00', 25000),
]

# Bi-weekly Middle East (policy=1, region=2)
TIERS[(1, 2)] = [
    (30000, '2.50', '0.00', '0.00', '0.00', 25000),
    (60000, '3.50', '1.20', '0.00', '0.00', 25000),
    (80000, '4.70', '1.60', '0.00', '0.00', 25000),
    (110000, '6.30', '2.10', '0.00', '0.00', 25000),
    (140000, '7.90', '2.60', '0.00', '0.00', 25000),
    (180000, '9.90', '2.60', '0.00', '0.00', 25000),
    (250000, '12.90', '4.30', '0.00', '0.00', 25000),
    (350000, '17.40', '5.80', '0.00', '0.00', 25000),
    (450000, '22.10', '7.40', '0.00', '0.00', 25000),
    (550000, '27.10', '9.00', '0.00', '0.00', 25000),
    (700000, '34.40', '11.50', '0.00', '0.00', 25000),
    (1100000, '66.00', '15.00', '4.00', '0.00', 25000),
    (1250000, '69.90', '20.00', '4.00', '0.00', 25000),
    (2200000, '112.20', '37.40', '5.00', '0.00', 25000),
    (2900000, '144.40', '48.10', '5.00', '0.00', 25000),
    (3500000, '168.00', '56.00', '5.00', '0.00', 25000),
    (4500000, '213.30', '71.10', '10.00', '0.00', 25000),
    (6000000, '280.80', '93.60', '10.00', '0.00', 25000),
    (7000000, '327.60', '109.20', '10.00', '0.00', 25000),
    (8000000, '374.40', '124.80', '15.00', '0.00', 25000),
    (9000000, '421.20', '140.40', '15.00', '0.00', 25000),
    (10500000, '491.40', '163.80', '15.00', '0.00', 25000),
    (12000000, '561.60', '187.20', '15.00', '0.00', 25000),
    (15000000, '702.00', '234.00', '20.00', '0.00', 25000),
    (19000000, '855.00', '285.00', '20.00', '0.00', 25000),
    (25000000, '1125.00', '375.00', '20.00', '0.00', 25000),
    (30000000, '1350.00', '450.00', '20.00', '0.00', 25000),
    (40000000, '1800.00', '600.00', '20.00', '0.00', 25000),
    (50000000, '2250.00', '750.00', '30.00', '0.00', 25000),
    (65000000, '2925.00', '975.00', '50.00', '0.00', 25000),
    (90000000, '4050.00', '1350.00', '50.00', '0.00', 25000),
    (120000000, '5256.00', '1752.00', '70.00', '0.00', 25000),
    (150000000, '6570.00', '2190.00', '100.00', '0.00', 25000),
    (200000000, '8760.00', '2920.00', '200.00', '0.00', 25000),
]

# Free English (policy=2, region=0)
TIERS[(2, 0)] = [
    (300000, '8.00', '2.00', '1.00', '0.00', 25000),
    (500000, '13.00', '3.00', '3.00', '0.00', 25000),
    (800000, '21.00', '4.00', '5.00', '1.00', 25000),
    (1400000, '38.00', '8.00', '7.00', '3.00', 25000),
    (2500000, '67.00', '13.00', '8.00', '5.00', 25000),
    (4500000, '121.00', '24.00', '9.00', '6.00', 25000),
    (7000000, '188.00', '38.00', '10.00', '8.00', 25000),
    (10000000, '268.00', '54.00', '20.00', '12.00', 25000),
    (20000000, '536.00', '107.00', '30.00', '15.00', 25000),
    (30000000, '804.00', '161.00', '50.00', '20.00', 25000),
    (50000000, '1339.00', '268.00', '80.00', '50.00', 25000),
]

# Free Middle East (policy=2, region=2)
TIERS[(2, 2)] = [
    (500000, '23.40', '7.80', '1.00', '0.00', 25000),
    (900000, '42.10', '14.00', '3.00', '0.00', 25000),
    (1500000, '70.20', '23.40', '5.00', '1.00', 25000),
    (2000000, '93.60', '31.20', '7.00', '3.00', 25000),
    (3000000, '140.40', '46.80', '8.00', '5.00', 25000),
    (5000000, '234.00', '78.00', '9.00', '6.00', 25000),
    (9000000, '421.20', '140.40', '10.00', '8.00', 25000),
    (15000000, '702.00', '234.00', '20.00', '12.00', 25000),
    (30000000, '1404.00', '468.00', '30.00', '15.00', 25000),
    (60000000, '2808.00', '936.00', '50.00', '20.00', 25000),
    (100000000, '4680.00', '1560.00', '80.00', '50.00', 25000),
]

FREE_DENOM = Decimal('16026')
BIWEEKLY_DENOM = Decimal('25000')

PERIOD_START = '2026-06-01 00:00:00'

def find_tier(diamonds, tiers_list):
    """Find the highest tier where diamonds >= threshold. Returns (index, tier_tuple) or None."""
    best = None
    best_idx = -1
    for i, t in enumerate(tiers_list):
        threshold = t[0]
        if diamonds >= threshold:
            best = t
            best_idx = i
    return best_idx, best

def calc_member(member_data, tiers):
    """Calculate host salary + president salary for one member."""
    m = member_data
    policy = m['member_policy']
    region = m['region']
    tier_list = tiers.get((policy, region), [])

    # ---- Attendance & Ratio ----
    is_biweekly = (policy == 1)
    ratio = Decimal('1.00')
    penalty_note = ''

    if is_biweekly:
        eff_days = m.get('effective_days', 0) or 0
        total_hours = Decimal(str(m.get('total_hours', 0) or 0))
        join_time = m.get('join_time', '')

        # First period protection
        if join_time and join_time > PERIOD_START:
            ratio = Decimal('1.00')
            penalty_note = 'first_period_protected'
        elif eff_days >= 6 and total_hours >= Decimal('12'):
            ratio = Decimal('1.00')
            penalty_note = 'qualified'
        else:
            ratio = Decimal('0.70')
            penalty_note = f'unqualified(eff={eff_days}d,hrs={total_hours})'

    # ---- HOST SALARY (gain_diamond + send_gain_diamond) ----
    host_diamonds = Decimal(str(m['gain_diamond'] + m['send_gain_diamond']))
    tier_idx, tier = find_tier(int(host_diamonds), tier_list)

    # tier tuple: (diamonds, host_salary, agency_owner_salary, host_tg_reward, agency_owner_tg_reward, excess_rate)
    if tier:
        threshold = Decimal(str(tier[0]))
        host_base = Decimal(tier[1])
        host_tg = Decimal(tier[3])   # host_tg_reward
        excess_rate = Decimal(str(tier[5]))
    else:
        threshold = Decimal('0')
        host_base = Decimal('0.00')
        host_tg = Decimal('0.00')
        excess_rate = BIWEEKLY_DENOM if is_biweekly else FREE_DENOM

    over = host_diamonds - threshold
    over_unit = over / excess_rate

    if is_biweekly:
        host_commission = floor2(over_unit)
    else:
        host_commission = floor2(over_unit * Decimal('0.75'))

    host_salary_raw = floor2(host_base + host_commission)
    host_tg_raw = host_tg
    host_total_raw = floor2(host_salary_raw + host_tg_raw)

    # Apply penalty
    host_salary = floor2(host_salary_raw * ratio)
    host_tg_final = floor2(host_tg_raw * ratio)
    host_total = floor2(host_total_raw * ratio)

    host_tier_level = tier_idx + 1 if tier else 0

    # ---- PRESIDENT SALARY (period_gain_coin) ----
    president_diamonds = Decimal(str(m['period_gain_coin']))
    p_tier_idx, p_tier = find_tier(int(president_diamonds), tier_list)

    if p_tier:
        p_threshold = Decimal(str(p_tier[0]))
        p_base = Decimal(p_tier[2])  # agency_owner_salary
        p_tg = Decimal(p_tier[4])    # agency_owner_tg_reward
        p_excess_rate = Decimal(str(p_tier[5]))
    else:
        p_threshold = Decimal('0')
        p_base = Decimal('0.00')
        p_tg = Decimal('0.00')
        p_excess_rate = BIWEEKLY_DENOM if is_biweekly else FREE_DENOM

    p_over = president_diamonds - p_threshold
    p_over_unit = p_over / p_excess_rate

    if is_biweekly:
        p_commission = Decimal('0.00')
    else:
        p_commission = floor2(p_over_unit * Decimal('0.25'))

    p_salary_raw = floor2(p_base + p_commission)
    p_tg_raw = p_tg
    p_total_raw = floor2(p_salary_raw + p_tg_raw)

    # President also gets penalty for bi-weekly
    p_salary = floor2(p_salary_raw * ratio) if is_biweekly else p_salary_raw
    p_tg_final = floor2(p_tg_raw * ratio) if is_biweekly else p_tg_raw
    p_total = floor2(p_total_raw * ratio) if is_biweekly else p_total_raw

    p_tier_level = p_tier_idx + 1 if p_tier else 0

    # ---- Advance Salary ----
    advance = Decimal(str(m.get('advance_salary_total_amount', 0) or 0))
    salary_balance = floor2(host_total - advance)

    return {
        'user_id': m['user_id'],
        'nickname': m['nickname'],
        'role': m['role'],
        'policy': policy,
        'region': region,
        'host_diamonds': int(host_diamonds),
        'host_tier': host_tier_level,
        'host_base': host_base,
        'host_commission': host_commission,
        'host_tg': host_tg_final,
        'host_salary': host_salary,  # base + commission (after penalty)
        'host_total': host_total,
        'president_diamonds': int(president_diamonds),
        'president_tier': p_tier_level,
        'president_base': p_base,
        'president_commission': p_commission,
        'president_tg': p_tg_final,
        'president_salary': p_salary,
        'president_total': p_total,
        'advance': advance,
        'salary_balance': salary_balance,
        'ratio': ratio,
        'penalty_note': penalty_note,
        'agent_shared_salary': p_total,  # What the guild gets from this member
    }

# ============================================================
# MEMBER DATA (from DB)
# ============================================================
MEMBERS = [
    # Agency 3485 - region=2, agency_policy=1
    {'user_id': 15393, 'nickname': 'u15393', 'role': 0, 'member_policy': 1, 'region': 2,
     'gain_diamond': 0, 'send_gain_diamond': 450000, 'period_gain_coin': 450000,
     'advance_salary_total_amount': 0, 'join_time': '2026-02-01T01:42:29',
     'effective_days': 0, 'total_hours': 4.07, 'agency_id': 3485},

    # Agency 3493 - region=0, agency_policy=1
    {'user_id': 15668, 'nickname': 'u15668', 'role': 2, 'member_policy': 1, 'region': 0,
     'gain_diamond': 999, 'send_gain_diamond': 0, 'period_gain_coin': 0,
     'advance_salary_total_amount': 0, 'join_time': '2026-03-13T02:36:41',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3493},

    # Agency 3529 - region=0, agency_policy=2
    {'user_id': 15672, 'nickname': 'leon', 'role': 0, 'member_policy': 2, 'region': 0,
     'gain_diamond': 3806880, 'send_gain_diamond': 0, 'period_gain_coin': 3806880,
     'advance_salary_total_amount': 0, 'join_time': '2026-03-15T23:11:23',
     'effective_days': 11, 'total_hours': 27.58, 'agency_id': 3529},
    {'user_id': 15686, 'nickname': 'u15686', 'role': 2, 'member_policy': 1, 'region': 0,
     'gain_diamond': 2889864, 'send_gain_diamond': 0, 'period_gain_coin': 2889864,
     'advance_salary_total_amount': 0, 'join_time': '2026-03-19T20:54:12',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3529},
    {'user_id': 15687, 'nickname': 'u15687', 'role': 2, 'member_policy': 2, 'region': 0,
     'gain_diamond': 1512864, 'send_gain_diamond': 0, 'period_gain_coin': 1512864,
     'advance_salary_total_amount': 0, 'join_time': '2026-03-19T20:54:15',
     'effective_days': 7, 'total_hours': 16.92, 'agency_id': 3529},
    {'user_id': 15689, 'nickname': 'u15689', 'role': 2, 'member_policy': 2, 'region': 0,
     'gain_diamond': 2000000, 'send_gain_diamond': 0, 'period_gain_coin': 0,
     'advance_salary_total_amount': 0, 'join_time': '2026-03-18T01:44:15',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3529},

    # Agency 3538 - region=2, agency_policy=2
    {'user_id': 15852, 'nickname': 'u15852', 'role': 0, 'member_policy': 2, 'region': 2,
     'gain_diamond': 0, 'send_gain_diamond': 0, 'period_gain_coin': 1888768,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-13T21:02:36',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3538},
    {'user_id': 15853, 'nickname': 'u15853', 'role': 2, 'member_policy': 1, 'region': 2,
     'gain_diamond': 1512864, 'send_gain_diamond': 0, 'period_gain_coin': 1512864,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-13T22:46:14',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3538},
    {'user_id': 15854, 'nickname': 'u15854', 'role': 2, 'member_policy': 2, 'region': 2,
     'gain_diamond': 1652672, 'send_gain_diamond': 0, 'period_gain_coin': 1652672,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-13T22:44:46',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3538},
    {'user_id': 15855, 'nickname': 'u15855', 'role': 2, 'member_policy': 1, 'region': 2,
     'gain_diamond': 5346880, 'send_gain_diamond': 0, 'period_gain_coin': 5346880,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-13T21:08:03',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3538},
    {'user_id': 15856, 'nickname': 'u15856', 'role': 2, 'member_policy': 2, 'region': 2,
     'gain_diamond': 0, 'send_gain_diamond': 0, 'period_gain_coin': 2124864,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-13T21:05:09',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3538},

    # Agency 3540 - region=2, agency_policy=1
    {'user_id': 15861, 'nickname': 'u15861', 'role': 0, 'member_policy': 1, 'region': 2,
     'gain_diamond': 3045504, 'send_gain_diamond': 0, 'period_gain_coin': 4104186,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-14T03:43:48',
     'effective_days': 0, 'total_hours': 0.10, 'agency_id': 3540},
    {'user_id': 15862, 'nickname': 'u15862', 'role': 2, 'member_policy': 1, 'region': 2,
     'gain_diamond': 3025728, 'send_gain_diamond': 0, 'period_gain_coin': 3025728,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-14T06:52:21',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3540},
    {'user_id': 15865, 'nickname': 'u15865', 'role': 2, 'member_policy': 2, 'region': 2,
     'gain_diamond': 1849056, 'send_gain_diamond': 0, 'period_gain_coin': 1849056,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-15T22:22:21',
     'effective_days': 0, 'total_hours': 1.82, 'agency_id': 3540},
    {'user_id': 15898, 'nickname': 'u15898', 'role': 2, 'member_policy': 2, 'region': 2,
     'gain_diamond': 2360960, 'send_gain_diamond': 0, 'period_gain_coin': 2360960,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-14T03:45:33',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3540},

    # Agency 3544 - region=0, agency_policy=2
    {'user_id': 16435, 'nickname': 'u16435', 'role': 0, 'member_policy': 2, 'region': 0,
     'gain_diamond': 1308813, 'send_gain_diamond': 0, 'period_gain_coin': 1308813,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-17T21:14:33',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3544},
    {'user_id': 16436, 'nickname': 'u16436', 'role': 2, 'member_policy': 1, 'region': 0,
     'gain_diamond': 1680960, 'send_gain_diamond': 0, 'period_gain_coin': 1680960,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-17T21:15:13',
     'effective_days': 0, 'total_hours': 0.10, 'agency_id': 3544},
    {'user_id': 16444, 'nickname': 'u16444', 'role': 2, 'member_policy': 2, 'region': 0,
     'gain_diamond': 1344768, 'send_gain_diamond': 0, 'period_gain_coin': 1344768,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-19T21:08:06',
     'effective_days': 0, 'total_hours': 0, 'agency_id': 3544},

    # Agency 3552 - region=0, agency_policy=2
    {'user_id': 16459, 'nickname': 'u16459', 'role': 0, 'member_policy': 2, 'region': 0,
     'gain_diamond': 472192, 'send_gain_diamond': 0, 'period_gain_coin': 472192,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-24T21:33:40',
     'effective_days': 10, 'total_hours': 26.00, 'agency_id': 3552},
    {'user_id': 16448, 'nickname': 'u16448', 'role': 2, 'member_policy': 1, 'region': 0,
     'gain_diamond': 504288, 'send_gain_diamond': 0, 'period_gain_coin': 504288,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-25T02:44:11',
     'effective_days': 4, 'total_hours': 11.50, 'agency_id': 3552},
    {'user_id': 16464, 'nickname': 'u16464', 'role': 2, 'member_policy': 2, 'region': 0,
     'gain_diamond': 1308813, 'send_gain_diamond': 0, 'period_gain_coin': 1308813,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-26T01:16:19',
     'effective_days': 8, 'total_hours': 19.42, 'agency_id': 3552},

    # Agency 3553 - region=0, agency_policy=2
    {'user_id': 16461, 'nickname': 'u16461', 'role': 0, 'member_policy': 2, 'region': 0,
     'gain_diamond': 0, 'send_gain_diamond': 450000, 'period_gain_coin': 450000,
     'advance_salary_total_amount': 0, 'join_time': '2026-05-25T08:08:23',
     'effective_days': 0, 'total_hours': 0.24, 'agency_id': 3553},
]

# Agency metadata
AGENCIES = {
    3485: {'name': '小太阳', 'owner_user_id': 15393, 'region': 2, 'policy': 1, 'borrowable_amount': 615, 'borrowed_amount': 0},
    3493: {'name': '公会test', 'owner_user_id': 15554, 'region': 0, 'policy': 1, 'borrowable_amount': 297, 'borrowed_amount': 0},
    3529: {'name': 'leon guild', 'owner_user_id': 15672, 'region': 0, 'policy': 2, 'borrowable_amount': 1596, 'borrowed_amount': 721},
    3538: {'name': '中东公会长自由政策', 'owner_user_id': 15852, 'region': 2, 'policy': 2, 'borrowable_amount': 990, 'borrowed_amount': 0},
    3540: {'name': '中东公会长双周政策', 'owner_user_id': 15861, 'region': 2, 'policy': 1, 'borrowable_amount': 940, 'borrowed_amount': 0},
    3544: {'name': '英语区公会长自由政策', 'owner_user_id': 16435, 'region': 0, 'policy': 2, 'borrowable_amount': 990, 'borrowed_amount': 0},
    3552: {'name': '英语区自由结算', 'owner_user_id': 16459, 'region': 0, 'policy': 2, 'borrowable_amount': 1120, 'borrowed_amount': 0},
    3553: {'name': '1111', 'owner_user_id': 16461, 'region': 0, 'policy': 2, 'borrowable_amount': 831, 'borrowed_amount': 0},
}

# ============================================================
# CALCULATE
# ============================================================
print("=" * 110)
print("GUILD SALARY REPORT — 2026-06-01 ~ 2026-06-15 (Current Period)")
print("=" * 110)

for agency_id in sorted(set(m['agency_id'] for m in MEMBERS)):
    ag = AGENCIES[agency_id]
    members = [m for m in MEMBERS if m['agency_id'] == agency_id]
    owner_id = ag['owner_user_id']

    print(f"\n{'='*110}")
    print(f"GUILD: [{agency_id}] {ag['name']}")
    print(f"  Owner: {owner_id} | Region: {'Middle East' if ag['region']==2 else 'English'} | "
          f"Policy: {'Bi-weekly' if ag['policy']==1 else 'Free'} | "
          f"Borrowable: ${ag['borrowable_amount']} | Borrowed: ${ag['borrowed_amount']}")
    print(f"{'='*110}")

    # --- Part 1: Member Salary ---
    print(f"\n  {'─'*105}")
    print(f"  PART 1: MEMBER SALARY DETAILS")
    print(f"  {'─'*105}")

    all_host_total = Decimal('0')
    all_agent_shared = Decimal('0')
    all_advance = Decimal('0')

    for m in members:
        r = calc_member(m, TIERS)
        m['_result'] = r

        all_host_total += r['host_total']
        all_agent_shared += r['agent_shared_salary']
        all_advance += r['advance']

        role_name = 'Owner' if r['role'] == 0 else 'Streamer'
        policy_name = 'Bi-weekly' if r['policy'] == 1 else 'Free'

        print(f"\n  ┌─ {r['nickname']} (user_id={r['user_id']}, {role_name}, {policy_name}, region={r['region']})")
        print(f"  │  Host Diamonds: {r['host_diamonds']:,} | Gain Coin (period): {r['president_diamonds']:,}")
        print(f"  │")
        print(f"  │  ── Host Salary ──")
        print(f"  │  Tier: Lv{r['host_tier']} | Base: ${r['host_base']} | Commission: ${r['host_commission']} | TG: ${r['host_tg']}")
        print(f"  │  Host Salary (base+comm): ${r['host_salary']} | Host Total: ${r['host_total']}")
        print(f"  │")
        print(f"  │  ── President Salary (Agent Shared) ──")
        print(f"  │  Tier: Lv{r['president_tier']} | Base: ${r['president_base']} | Commission: ${r['president_commission']} | TG: ${r['president_tg']}")
        print(f"  │  Agent Shared Salary: ${r['agent_shared_salary']}")
        print(f"  │")
        print(f"  │  ── Summary ──")
        print(f"  │  Advance: ${r['advance']} | Salary Balance: ${r['salary_balance']}")
        print(f"  │  Ratio: {r['ratio']} ({r['penalty_note']})")
        print(f"  └─ Member Total (Host+President): ${floor2(r['host_total'] + r['agent_shared_salary'])}")

    # --- Part 2: Guild Summary ---
    print(f"\n  {'─'*105}")
    print(f"  PART 2: GUILD-LEVEL SUMMARY")
    print(f"  {'─'*105}")

    # Find owner's result
    owner_result = None
    for m in members:
        if m['user_id'] == owner_id:
            owner_result = m['_result']
            break

    # Agency total salary = All hosts salary + Agent Commission
    # All hosts salary = sum of all host_total (including owner as host)
    agency_total_salary = floor2(all_host_total + all_agent_shared)
    agency_advance = all_advance
    agency_salary_balance = floor2(agency_total_salary - agency_advance)

    # Agent as host salary (owner's host salary, without TG)
    agent_as_host_salary = owner_result['host_salary'] if owner_result else Decimal('0')
    agent_tg = owner_result['host_tg'] if owner_result else Decimal('0')
    agent_commission = all_agent_shared
    agent_total = floor2(agent_as_host_salary + agent_tg + agent_commission)
    agent_advance_host = owner_result['advance'] if owner_result else Decimal('0')
    agent_salary_balance_val = floor2(agent_total - agent_advance_host)

    print(f"\n  All Hosts Salary (sum host_total):                  ${all_host_total}")
    print(f"  Agent Commission (sum agent_shared):                ${all_agent_shared}")
    print(f"  Agency Total Salary:                                ${agency_total_salary}")
    print(f"  Agency Advance Salary:                              ${agency_advance}")
    print(f"  Agency Total Salary Balance:                        ${agency_salary_balance}")
    print(f"")
    print(f"  Agent as Host Salary (owner, base+comm, no TG):     ${agent_as_host_salary}")
    print(f"  Agent TG Reward (owner):                            ${agent_tg}")
    print(f"  Agent Commission (sum all agent_shared):            ${agent_commission}")
    print(f"  Agent Total Salary:                                 ${agent_total}")
    print(f"  Agent Advance Salary:                               ${agent_advance_host}")
    print(f"  Agent Salary Balance:                               ${agent_salary_balance_val}")
    print(f"  Agent Borrowed Amount:                              ${ag['borrowed_amount']}")
    print(f"  Agent Borrowable Amount:                            ${ag['borrowable_amount']}")

    # --- Part 3: Surplus ---
    print(f"\n  {'─'*105}")
    print(f"  PART 3: GUILD SURPLUS (Owner={owner_id})")
    print(f"  {'─'*105}")

    # 本期薪资 = Agent as host Salary + Agent TG Reward + Agent Commission
    period_salary = floor2(agent_as_host_salary + agent_tg + agent_commission)
    # 本期借支 = borrowed_amount (from agency table)
    period_borrow = Decimal(str(ag['borrowed_amount']))
    # 本期实际工资 = 本期薪资 - 本期借支 - 历史欠款
    # For historical debt, query app_payer_agency_owner_surplus
    # We'll set it to 0 for now and note it

    print(f"\n  本期薪资 (Agent as host + TG + Commission):  ${period_salary}")
    print(f"  本期借支 (borrowed_amount):                   ${period_borrow}")
    print(f"  历史欠款:                                      [need surplus archive query]")
    print(f"  本期实际工资 (薪资 - 借支 - 历史欠款):        ${floor2(period_salary - period_borrow)} (before historical debt)")
    print(f"  本期盈余 (薪资 - 借支):                        ${floor2(period_salary - period_borrow)}")

print(f"\n{'='*110}")
print("END OF REPORT")
print(f"{'='*110}")
