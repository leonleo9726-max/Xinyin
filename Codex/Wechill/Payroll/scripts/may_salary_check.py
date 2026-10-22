"""Check May 2026 settlement status and calculate pending salaries."""
import sys
sys.path.insert(0, '.')
from decimal import Decimal, ROUND_DOWN

def floor2(d):
    return d.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

# ── User 15689 data ──
# gain_diamond = 300000, gain_coin = 0
# policy = 2 (Liberal), region = 0 (English)
# Tier: Level 1 matched (diamonds=300000)

LIBERAL_DENOM = Decimal('16026')
HOST_RATE = Decimal('0.75')
PRESIDENT_RATE = Decimal('0.25')

gain_diamond = Decimal('300000')
gain_coin = Decimal('0')

# Host tier: Level 1, threshold=300000
host_threshold = Decimal('300000')
host_base = Decimal('8.00')
host_tg = Decimal('1.00')

over_host = gain_diamond - host_threshold  # 0
host_over_unit = over_host / LIBERAL_DENOM
host_commission = floor2(host_over_unit * HOST_RATE)
host_total = floor2(host_base + host_commission + host_tg)

print("=== User 15689 (user_number=8526429) ===")
print(f"Agency: 3529 (leon guild), Region: English (0), Policy: Liberal (2)")
print(f"gain_diamond: {gain_diamond}, gain_coin: {gain_coin}")
print()
print("--- Host Salary (gain_diamond=300000) ---")
print(f"  Tier: Level 1 (threshold=300000)")
print(f"  Base Salary: {host_base}")
print(f"  TG Reward:   {host_tg}")
print(f"  Over-tier diamonds: {over_host}")
print(f"  Over-tier units:    {floor2(host_over_unit)}")
print(f"  Over-tier commission: {host_commission}  (= {floor2(host_over_unit)} x 0.75)")
print(f"  Host Total: {host_total}")
print()

# President share (gain_coin=0, below Level 1)
president_threshold = Decimal('0')
president_base = Decimal('0.00')
president_tg = Decimal('0.00')

over_president = gain_coin - president_threshold  # 0
president_over_unit = over_president / LIBERAL_DENOM
president_commission = floor2(president_over_unit * PRESIDENT_RATE)
president_total = floor2(president_base + president_commission + president_tg)

print("--- President Share (gain_coin=0) ---")
print(f"  Tier: Below Level 1 (threshold=300000)")
print(f"  No-tier rule: base=0, TG=0, over-tier from 0")
print(f"  Over-tier coins: {over_president}")
print(f"  Over-tier units: {floor2(president_over_unit)}")
print(f"  Over-tier commission: {president_commission}")
print(f"  President Total: {president_total}")
print()

user_total = floor2(host_total + president_total)
print(f"=== USER TOTAL: {user_total} ===")
print()
print("Qualification: Liberal policy -> default qualified, no penalty")
print("Period: 2026-05-16 to 2026-05-31")
print("No daily summary data found for this period.")

# ── Summary ──
print()
print("=" * 60)
print("ROOT CAUSE: Why no May settlement data")
print("=" * 60)
print()
print("1. April settlement (generated 2026-05-02) reset gain_diamond/gain_coin")
print("   to 0 for all 23 settled guild members across 9 agencies.")
print()
print("2. In May, only 1 active guild member generated new diamond flow:")
print("   - user_id=15689 (8526429), agency=3529 (leon guild)")
print("   - gain_diamond=300,000, gain_coin=0")
print("   - Calculated salary: $9.00")
print()
print("3. All other active guild members have gain_diamond=0 and gain_coin=0,")
print("   meaning no activity since the April reset.")
print()
print("4. The settlement batch job (backend service) was not triggered for May.")
print("   Even with only 1 eligible user, a settlement run should create records")
print("   in app_payer_party_agency_salary_detail and app_payer_party_host_salary_detail.")
print()
print("5. Additionally, there are 86 users with gain_diamond>0 who are NOT in")
print("   any active guild (independent streamers) -- they don't go through")
print("   guild settlement.")
