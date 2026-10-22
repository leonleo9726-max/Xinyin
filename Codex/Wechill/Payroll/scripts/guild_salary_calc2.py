# -*- coding: ascii -*-
"""
Guild Salary Calculation - 2026-06-01 to 2026-06-15
"""
from decimal import Decimal, ROUND_DOWN
import json, sys

def floor2(d):
    return d.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

# Tier configs: (policy, region) -> [(diamonds, host_salary, agency_owner_salary, host_tg_reward, agency_owner_tg_reward, excess_rate), ...]
TIERS = {}
TIERS[(1, 0)] = [(10000,'0.40','0.00','0.00','0.00',25000),(30000,'1.30','1.00','0.00','0.00',25000),(50000,'2.20','1.00','0.00','0.00',25000),(80000,'3.60','1.00','0.00','0.00',25000),(110000,'4.90','2.00','0.00','0.00',25000),(140000,'6.30','2.00','0.00','0.00',25000),(190000,'8.50','3.00','0.00','0.00',25000),(250000,'11.20','4.00','0.00','0.00',25000),(350000,'15.60','6.00','0.00','0.00',25000),(450000,'20.10','8.00','0.00','0.00',25000),(500000,'22.30','9.00','0.00','0.00',25000),(700000,'31.30','10.00','5.00','0.00',25000),(1000000,'44.60','14.00','8.00','0.00',25000),(1500000,'67.00','22.00','10.00','0.00',25000),(2000000,'89.30','30.00','10.00','0.00',25000),(3000000,'133.90','48.00','10.00','0.00',25000),(4000000,'178.60','61.00','20.00','0.00',25000),(5000000,'223.20','78.00','20.00','0.00',25000),(6000000,'267.90','96.00','20.00','0.00',25000),(7000000,'312.50','114.00','20.00','0.00',25000),(8500000,'379.50','140.00','20.00','0.00',25000),(10500000,'468.80','176.00','20.00','0.00',25000),(11500000,'513.40','188.00','30.00','0.00',25000),(14000000,'625.00','233.00','30.00','0.00',25000),(17000000,'758.90','286.00','30.00','0.00',25000),(22000000,'982.10','374.00','30.00','0.00',25000),(27000000,'1205.40','452.00','50.00','0.00',25000),(35000000,'1562.50','594.00','50.00','0.00',25000),(45000000,'2008.90','771.00','50.00','0.00',25000),(60000000,'2678.60','1036.00','50.00','0.00',25000),(70000000,'3125.00','1213.00','50.00','0.00',25000),(90000000,'4017.90','1541.00','100.00','0.00',25000),(120000000,'5357.10','2071.00','100.00','0.00',25000),(150000000,'6696.40','2602.00','100.00','0.00',25000)]
TIERS[(1, 2)] = [(30000,'2.50','0.00','0.00','0.00',25000),(60000,'3.50','1.20','0.00','0.00',25000),(80000,'4.70','1.60','0.00','0.00',25000),(110000,'6.30','2.10','0.00','0.00',25000),(140000,'7.90','2.60','0.00','0.00',25000),(180000,'9.90','2.60','0.00','0.00',25000),(250000,'12.90','4.30','0.00','0.00',25000),(350000,'17.40','5.80','0.00','0.00',25000),(450000,'22.10','7.40','0.00','0.00',25000),(550000,'27.10','9.00','0.00','0.00',25000),(700000,'34.40','11.50','0.00','0.00',25000),(1100000,'66.00','15.00','4.00','0.00',25000),(1250000,'69.90','20.00','4.00','0.00',25000),(2200000,'112.20','37.40','5.00','0.00',25000),(2900000,'144.40','48.10','5.00','0.00',25000),(3500000,'168.00','56.00','5.00','0.00',25000),(4500000,'213.30','71.10','10.00','0.00',25000),(6000000,'280.80','93.60','10.00','0.00',25000),(7000000,'327.60','109.20','10.00','0.00',25000),(8000000,'374.40','124.80','15.00','0.00',25000),(9000000,'421.20','140.40','15.00','0.00',25000),(10500000,'491.40','163.80','15.00','0.00',25000),(12000000,'561.60','187.20','15.00','0.00',25000),(15000000,'702.00','234.00','20.00','0.00',25000),(19000000,'855.00','285.00','20.00','0.00',25000),(25000000,'1125.00','375.00','20.00','0.00',25000),(30000000,'1350.00','450.00','20.00','0.00',25000),(40000000,'1800.00','600.00','20.00','0.00',25000),(50000000,'2250.00','750.00','30.00','0.00',25000),(65000000,'2925.00','975.00','50.00','0.00',25000),(90000000,'4050.00','1350.00','50.00','0.00',25000),(120000000,'5256.00','1752.00','70.00','0.00',25000),(150000000,'6570.00','2190.00','100.00','0.00',25000),(200000000,'8760.00','2920.00','200.00','0.00',25000)]
TIERS[(2, 0)] = [(300000,'8.00','2.00','1.00','0.00',25000),(500000,'13.00','3.00','3.00','0.00',25000),(800000,'21.00','4.00','5.00','1.00',25000),(1400000,'38.00','8.00','7.00','3.00',25000),(2500000,'67.00','13.00','8.00','5.00',25000),(4500000,'121.00','24.00','9.00','6.00',25000),(7000000,'188.00','38.00','10.00','8.00',25000),(10000000,'268.00','54.00','20.00','12.00',25000),(20000000,'536.00','107.00','30.00','15.00',25000),(30000000,'804.00','161.00','50.00','20.00',25000),(50000000,'1339.00','268.00','80.00','50.00',25000)]
TIERS[(2, 2)] = [(500000,'23.40','7.80','1.00','0.00',25000),(900000,'42.10','14.00','3.00','0.00',25000),(1500000,'70.20','23.40','5.00','1.00',25000),(2000000,'93.60','31.20','7.00','3.00',25000),(3000000,'140.40','46.80','8.00','5.00',25000),(5000000,'234.00','78.00','9.00','6.00',25000),(9000000,'421.20','140.40','10.00','8.00',25000),(15000000,'702.00','234.00','20.00','12.00',25000),(30000000,'1404.00','468.00','30.00','15.00',25000),(60000000,'2808.00','936.00','50.00','20.00',25000),(100000000,'4680.00','1560.00','80.00','50.00',25000)]

FREE_DENOM = Decimal('16026')
BIWEEKLY_DENOM = Decimal('25000')
PERIOD_START = '2026-06-01 00:00:00'

def find_tier(diamonds, tiers_list):
    best = None
    best_idx = -1
    for i, t in enumerate(tiers_list):
        if diamonds >= t[0]:
            best = t
            best_idx = i
    return best_idx, best

def calc(m, tiers):
    policy = m['member_policy']
    region = m['region']
    tier_list = tiers.get((policy, region), [])
    is_biweekly = (policy == 1)

    # ---- Ratio ----
    ratio = Decimal('1.00')
    penalty_note = ''
    if is_biweekly:
        eff = m.get('effective_days', 0) or 0
        hrs = Decimal(str(m.get('total_hours', 0) or 0))
        jt = m.get('join_time', '')
        if jt and jt > PERIOD_START:
            penalty_note = 'first_period_protected'
        elif eff >= 6 and hrs >= Decimal('12'):
            penalty_note = 'qualified'
        else:
            ratio = Decimal('0.70')
            penalty_note = 'unqualified(eff=%dd,hrs=%s)' % (eff, hrs)

    # ---- Host Salary ----
    hd = Decimal(str(m['gain_diamond'] + m['send_gain_diamond']))
    ti, t = find_tier(int(hd), tier_list)
    er = BIWEEKLY_DENOM if is_biweekly else FREE_DENOM
    if t:
        th = Decimal(str(t[0])); hb = Decimal(t[1]); htg = Decimal(t[3])
    else:
        th = Decimal('0'); hb = Decimal('0.00'); htg = Decimal('0.00')

    ov = hd - th
    ou = ov / er
    hc = floor2(ou) if is_biweekly else floor2(ou * Decimal('0.75'))
    hsr = floor2(hb + hc)
    htr = htg
    httr = floor2(hsr + htr)

    hs = floor2(hsr * ratio)
    htf = floor2(htr * ratio)
    htt = floor2(httr * ratio)
    htl = ti + 1 if t else 0

    # ---- President Salary ----
    pd = Decimal(str(m['period_gain_coin']))
    pti, pt = find_tier(int(pd), tier_list)
    per = BIWEEKLY_DENOM if is_biweekly else FREE_DENOM
    if pt:
        pth = Decimal(str(pt[0])); pb = Decimal(pt[2]); ptg = Decimal(pt[4])
    else:
        pth = Decimal('0'); pb = Decimal('0.00'); ptg = Decimal('0.00')

    pov = pd - pth
    pou = pov / per
    pc = Decimal('0.00') if is_biweekly else floor2(pou * Decimal('0.25'))
    psr = floor2(pb + pc)
    ptr = ptg
    pttr = floor2(psr + ptr)

    if is_biweekly:
        ps = floor2(psr * ratio); ptf = floor2(ptr * ratio); ptt = floor2(pttr * ratio)
    else:
        ps = psr; ptf = ptr; ptt = pttr
    ptl = pti + 1 if pt else 0

    adv = Decimal(str(m.get('advance_salary_total_amount', 0) or 0))
    sb = floor2(htt - adv)

    return {
        'user_id': m['user_id'], 'nickname': m['nickname'], 'role': m['role'],
        'policy': policy, 'region': region,
        'host_diamonds': int(hd), 'host_tier': htl, 'host_base': str(hb),
        'host_commission': str(hc), 'host_tg': str(htf), 'host_salary': str(hs),
        'host_total': str(htt),
        'president_diamonds': int(pd), 'president_tier': ptl, 'president_base': str(pb),
        'president_commission': str(pc), 'president_tg': str(ptf),
        'president_salary': str(ps), 'president_total': str(ptt),
        'advance': str(adv), 'salary_balance': str(sb),
        'ratio': str(ratio), 'penalty_note': penalty_note,
        'agent_shared_salary': str(ptt),
    }

MEMBERS = [
    {'user_id':15393,'nickname':'u15393','role':0,'member_policy':1,'region':2,'gain_diamond':0,'send_gain_diamond':450000,'period_gain_coin':450000,'advance_salary_total_amount':0,'join_time':'2026-02-01','effective_days':0,'total_hours':4.07,'agency_id':3485},
    {'user_id':15668,'nickname':'u15668','role':2,'member_policy':1,'region':0,'gain_diamond':999,'send_gain_diamond':0,'period_gain_coin':0,'advance_salary_total_amount':0,'join_time':'2026-03-13','effective_days':0,'total_hours':0,'agency_id':3493},
    {'user_id':15672,'nickname':'leon','role':0,'member_policy':2,'region':0,'gain_diamond':3806880,'send_gain_diamond':0,'period_gain_coin':3806880,'advance_salary_total_amount':0,'join_time':'2026-03-15','effective_days':11,'total_hours':27.58,'agency_id':3529},
    {'user_id':15686,'nickname':'u15686','role':2,'member_policy':1,'region':0,'gain_diamond':2889864,'send_gain_diamond':0,'period_gain_coin':2889864,'advance_salary_total_amount':0,'join_time':'2026-03-19','effective_days':0,'total_hours':0,'agency_id':3529},
    {'user_id':15687,'nickname':'u15687','role':2,'member_policy':2,'region':0,'gain_diamond':1512864,'send_gain_diamond':0,'period_gain_coin':1512864,'advance_salary_total_amount':0,'join_time':'2026-03-19','effective_days':7,'total_hours':16.92,'agency_id':3529},
    {'user_id':15689,'nickname':'u15689','role':2,'member_policy':2,'region':0,'gain_diamond':2000000,'send_gain_diamond':0,'period_gain_coin':0,'advance_salary_total_amount':0,'join_time':'2026-03-18','effective_days':0,'total_hours':0,'agency_id':3529},
    {'user_id':15852,'nickname':'u15852','role':0,'member_policy':2,'region':2,'gain_diamond':0,'send_gain_diamond':0,'period_gain_coin':1888768,'advance_salary_total_amount':0,'join_time':'2026-05-13','effective_days':0,'total_hours':0,'agency_id':3538},
    {'user_id':15853,'nickname':'u15853','role':2,'member_policy':1,'region':2,'gain_diamond':1512864,'send_gain_diamond':0,'period_gain_coin':1512864,'advance_salary_total_amount':0,'join_time':'2026-05-13','effective_days':0,'total_hours':0,'agency_id':3538},
    {'user_id':15854,'nickname':'u15854','role':2,'member_policy':2,'region':2,'gain_diamond':1652672,'send_gain_diamond':0,'period_gain_coin':1652672,'advance_salary_total_amount':0,'join_time':'2026-05-13','effective_days':0,'total_hours':0,'agency_id':3538},
    {'user_id':15855,'nickname':'u15855','role':2,'member_policy':1,'region':2,'gain_diamond':5346880,'send_gain_diamond':0,'period_gain_coin':5346880,'advance_salary_total_amount':0,'join_time':'2026-05-13','effective_days':0,'total_hours':0,'agency_id':3538},
    {'user_id':15856,'nickname':'u15856','role':2,'member_policy':2,'region':2,'gain_diamond':0,'send_gain_diamond':0,'period_gain_coin':2124864,'advance_salary_total_amount':0,'join_time':'2026-05-13','effective_days':0,'total_hours':0,'agency_id':3538},
    {'user_id':15861,'nickname':'u15861','role':0,'member_policy':1,'region':2,'gain_diamond':3045504,'send_gain_diamond':0,'period_gain_coin':4104186,'advance_salary_total_amount':0,'join_time':'2026-05-14','effective_days':0,'total_hours':0.10,'agency_id':3540},
    {'user_id':15862,'nickname':'u15862','role':2,'member_policy':1,'region':2,'gain_diamond':3025728,'send_gain_diamond':0,'period_gain_coin':3025728,'advance_salary_total_amount':0,'join_time':'2026-05-14','effective_days':0,'total_hours':0,'agency_id':3540},
    {'user_id':15865,'nickname':'u15865','role':2,'member_policy':2,'region':2,'gain_diamond':1849056,'send_gain_diamond':0,'period_gain_coin':1849056,'advance_salary_total_amount':0,'join_time':'2026-05-15','effective_days':0,'total_hours':1.82,'agency_id':3540},
    {'user_id':15898,'nickname':'u15898','role':2,'member_policy':2,'region':2,'gain_diamond':2360960,'send_gain_diamond':0,'period_gain_coin':2360960,'advance_salary_total_amount':0,'join_time':'2026-05-14','effective_days':0,'total_hours':0,'agency_id':3540},
    {'user_id':16435,'nickname':'u16435','role':0,'member_policy':2,'region':0,'gain_diamond':1308813,'send_gain_diamond':0,'period_gain_coin':1308813,'advance_salary_total_amount':0,'join_time':'2026-05-17','effective_days':0,'total_hours':0,'agency_id':3544},
    {'user_id':16436,'nickname':'u16436','role':2,'member_policy':1,'region':0,'gain_diamond':1680960,'send_gain_diamond':0,'period_gain_coin':1680960,'advance_salary_total_amount':0,'join_time':'2026-05-17','effective_days':0,'total_hours':0.10,'agency_id':3544},
    {'user_id':16444,'nickname':'u16444','role':2,'member_policy':2,'region':0,'gain_diamond':1344768,'send_gain_diamond':0,'period_gain_coin':1344768,'advance_salary_total_amount':0,'join_time':'2026-05-19','effective_days':0,'total_hours':0,'agency_id':3544},
    {'user_id':16459,'nickname':'u16459','role':0,'member_policy':2,'region':0,'gain_diamond':472192,'send_gain_diamond':0,'period_gain_coin':472192,'advance_salary_total_amount':0,'join_time':'2026-05-24','effective_days':10,'total_hours':26.00,'agency_id':3552},
    {'user_id':16448,'nickname':'u16448','role':2,'member_policy':1,'region':0,'gain_diamond':504288,'send_gain_diamond':0,'period_gain_coin':504288,'advance_salary_total_amount':0,'join_time':'2026-05-25','effective_days':4,'total_hours':11.50,'agency_id':3552},
    {'user_id':16464,'nickname':'u16464','role':2,'member_policy':2,'region':0,'gain_diamond':1308813,'send_gain_diamond':0,'period_gain_coin':1308813,'advance_salary_total_amount':0,'join_time':'2026-05-26','effective_days':8,'total_hours':19.42,'agency_id':3552},
    {'user_id':16461,'nickname':'u16461','role':0,'member_policy':2,'region':0,'gain_diamond':0,'send_gain_diamond':450000,'period_gain_coin':450000,'advance_salary_total_amount':0,'join_time':'2026-05-25','effective_days':0,'total_hours':0.24,'agency_id':3553},
]

AGENCIES = {
    3485: {'name':'XiaoTaiYang','owner':15393,'region':2,'policy':1,'borrowable':615,'borrowed':0},
    3493: {'name':'GuildTest','owner':15554,'region':0,'policy':1,'borrowable':297,'borrowed':0},
    3529: {'name':'leon guild','owner':15672,'region':0,'policy':2,'borrowable':1596,'borrowed':721},
    3538: {'name':'ME_Free_President','owner':15852,'region':2,'policy':2,'borrowable':990,'borrowed':0},
    3540: {'name':'ME_Biweekly_President','owner':15861,'region':2,'policy':1,'borrowable':940,'borrowed':0},
    3544: {'name':'EN_Free_President','owner':16435,'region':0,'policy':2,'borrowable':990,'borrowed':0},
    3552: {'name':'EN_Free_Settlement','owner':16459,'region':0,'policy':2,'borrowable':1120,'borrowed':0},
    3553: {'name':'1111','owner':16461,'region':0,'policy':2,'borrowable':831,'borrowed':0},
}

# Surplus history (from DB query)
SURPLUS = {
    15554: {'historical_debt': '0.00', 'last_actual': '11748.94'},   # agency 3493, settled with debt cleared
    15672: {'historical_debt': '649.15', 'last_actual': '-649.15'},   # agency 3529
    15852: {'historical_debt': '0.00', 'last_actual': '123.85'},      # agency 3538
    15861: {'historical_debt': '0.00', 'last_actual': '42.16'},       # agency 3540
    16459: {'historical_debt': '0.00', 'last_actual': '561.88'},      # agency 3552
}

# Calculate
results = {}
for m in MEMBERS:
    r = calc(m, TIERS)
    aid = m['agency_id']
    if aid not in results:
        results[aid] = {'members': [], 'sum_host_total': Decimal('0'), 'sum_agent_shared': Decimal('0'), 'sum_advance': Decimal('0')}
    results[aid]['members'].append(r)
    results[aid]['sum_host_total'] += Decimal(r['host_total'])
    results[aid]['sum_agent_shared'] += Decimal(r['agent_shared_salary'])
    results[aid]['sum_advance'] += Decimal(r['advance'])

# Output
for aid in sorted(results.keys()):
    ag = AGENCIES[aid]
    rr = results[aid]
    owner_id = ag['owner']
    owner_r = None
    for m in rr['members']:
        if m['user_id'] == owner_id:
            owner_r = m
            break

    print('=' * 110)
    print('GUILD: [%d] %s  |  Owner: %d  |  Region: %s  |  Policy: %s  |  Borrowable: $%d  |  Borrowed: $%d' % (
        aid, ag['name'], owner_id,
        'Middle East' if ag['region']==2 else 'English',
        'Bi-weekly' if ag['policy']==1 else 'Free',
        ag['borrowable'], ag['borrowed']))
    print('=' * 110)

    # PART 1
    print('\n--- PART 1: MEMBER SALARY DETAILS ---')
    for r in rr['members']:
        role_s = 'Owner' if r['role']==0 else 'Streamer'
        pol_s = 'BW' if r['policy']==1 else 'Free'
        print('  [%s] uid=%d %s %s R%d' % (r['nickname'], r['user_id'], role_s, pol_s, r['region']))
        print('       Host: diamonds=%(host_diamonds)d tier=Lv%(host_tier)d base=$%(host_base)s comm=$%(host_commission)s tg=$%(host_tg)s | HostSalary=$%(host_salary)s HostTotal=$%(host_total)s' % r)
        print('       Pres: diamonds=%(president_diamonds)d tier=Lv%(president_tier)d base=$%(president_base)s comm=$%(president_commission)s tg=$%(president_tg)s | AgentShared=$%(agent_shared_salary)s' % r)
        print('       Adv=$%s Bal=$%s Ratio=%s (%s) | MemberTotal=$%s' % (r['advance'], r['salary_balance'], r['ratio'], r['penalty_note'], floor2(Decimal(r['host_total'])+Decimal(r['agent_shared_salary']))))

    # PART 2
    all_ht = rr['sum_host_total']
    all_as = rr['sum_agent_shared']
    all_adv = rr['sum_advance']
    ag_total = floor2(all_ht + all_as)
    ag_bal = floor2(ag_total - all_adv)

    if owner_r:
        aahs = Decimal(owner_r['host_salary'])
        atg = Decimal(owner_r['host_tg'])
        acomm = all_as
        atotal = floor2(aahs + atg + acomm)
        aadv = Decimal(owner_r['advance'])
        abal = floor2(atotal - aadv)
    else:
        aahs = Decimal('0'); atg = Decimal('0'); acomm = all_as
        atotal = floor2(acomm); aadv = Decimal('0'); abal = atotal

    print('\n--- PART 2: GUILD-LEVEL SUMMARY ---')
    print('  All Hosts Salary (sum host_total):          $%s' % all_ht)
    print('  Agent Commission (sum agent_shared):        $%s' % all_as)
    print('  Agency Total Salary:                        $%s' % ag_total)
    print('  Agency Advance Salary:                      $%s' % all_adv)
    print('  Agency Total Salary Balance:                $%s' % ag_bal)
    print('')
    print('  Agent as Host Salary (owner, base+comm):    $%s' % aahs)
    print('  Agent TG Reward (owner):                    $%s' % atg)
    print('  Agent Commission (sum all agent_shared):    $%s' % acomm)
    print('  Agent Total Salary:                         $%s' % atotal)
    print('  Agent Advance Salary:                       $%s' % aadv)
    print('  Agent Salary Balance:                       $%s' % abal)
    print('  Agent Borrowed Amount:                      $%d' % ag['borrowed'])
    print('  Agent Borrowable Amount:                    $%d' % ag['borrowable'])

    # PART 3
    period_salary = floor2(aahs + atg + acomm)
    period_borrow = Decimal(str(ag['borrowed']))

    # Historical debt
    hist_debt_info = SURPLUS.get(owner_id, {})
    hist_debt = Decimal(hist_debt_info.get('historical_debt', '0'))
    if hist_debt == 0 and hist_debt_info.get('last_actual', '').startswith('-'):
        hist_debt = abs(Decimal(hist_debt_info['last_actual']))

    period_actual = floor2(period_salary - period_borrow - hist_debt)
    surplus = floor2(period_salary - period_borrow)

    print('\n--- PART 3: GUILD SURPLUS (Owner=%d) ---' % owner_id)
    print('  Period Salary (Agent as host + TG + Commission): $%s' % period_salary)
    print('  Period Borrow (borrowed_amount):                  $%s' % period_borrow)
    print('  Historical Debt (from surplus archive):           $%s' % hist_debt)
    print('  Period Actual Salary (salary-borrow-debt):        $%s' % period_actual)
    print('  Surplus (salary - borrow):                        $%s' % surplus)
    if period_actual < 0:
        print('  ** WARNING: Period Actual Salary < 0 -> would carry over $%s to next period **' % abs(period_actual))
    print('')

print('=' * 110)
print('END OF REPORT')
