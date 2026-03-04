# main.py
from xer_parser.xer_parser import XERParser
from metrics.open_ends          import check_open_ends
from metrics.leads              import check_leads
from metrics.lags               import check_lags
from metrics.relationship_types import check_relationship_types
from metrics.hard_constraints   import check_hard_constraints
from metrics.high_float         import check_high_float
from metrics.negative_float     import check_negative_float
from metrics.long_duration      import check_long_duration
from metrics.invalid_dates      import check_invalid_dates
from metrics.resources          import check_resources
from metrics.remaining_metrics  import (check_logic_density,
                                        check_missed_activities,
                                        check_summary_tasks,
                                        check_critical_path)
from engineering.mechanical_checks import check_mechanical_sequence
from engineering.energy_checks     import check_energy_dependencies
from metrics.redundant_relationships import check_redundant_relationships

# ── Load Schedule ──────────────────────────────────────────
parser = XERParser("data/sample_schedule.xer")
parser.parse()
activities    = parser.activities
relationships = parser.relationships

# ── Helper ─────────────────────────────────────────────────
def print_result(result):
    icon = "✅" if result['status'] == "PASS" else "❌"
    print(f"  {icon} {result['metric']}")
    print(f"     Status     : {result['status']}")
    print(f"     Violations : {result['violations']} / {result['total']} ({result['percentage']}%)")
    print(f"     Threshold  : {result['threshold']}")
    if result['details']:
        for v in result['details']:
            # Handle both activity-level and relationship-level violations
            if 'task_code' in v:
                label = v['task_code']
            elif 'pred_code' in v and 'succ_code' in v:
                label = f"{v['pred_code']}→{v['succ_code']}"
            else:
                label = "?"
            print(f"       ↳ [{label}] {v['issue']}")
    else:
        print(f"     ✔ No violations found")
    print()

# ── Run All 14 Metrics ─────────────────────────────────────
results = [
    check_open_ends(activities),
    check_leads(activities, relationships),
    check_lags(activities, relationships),
    check_relationship_types(activities, relationships),
    check_hard_constraints(activities),
    check_high_float(activities),
    check_negative_float(activities),
    check_long_duration(activities),
    check_invalid_dates(activities),
    check_resources(activities),
    check_logic_density(activities),
    check_missed_activities(activities, data_date_str=None),
    check_summary_tasks(activities),
    check_critical_path(activities),
    check_redundant_relationships(activities, relationships),
]

print(f"\n{'='*60}")
print(f"  SCHEDULE QUALITY VALIDATION REPORT")
print(f"  Activities: {len(activities)}  |  Relationships: {len(relationships)}")
print(f"{'='*60}\n")

for r in results:
    print_result(r)

# ── Overall Score ──────────────────────────────────────────
passed = sum(1 for r in results if r['status'] == "PASS")
total  = len(results)
score  = round((passed / total) * 100)

print(f"{'='*60}")
print(f"  OVERALL SCORE : {passed}/{total} metrics passing ({score}%)")
if score >= 80:
    print(f"  GRADE         : ✅ GOOD — Schedule quality is acceptable")
elif score >= 60:
    print(f"  GRADE         : ⚠️  FAIR — Schedule needs improvement")
else:
    print(f"  GRADE         : ❌ POOR — Schedule requires major revision")
print(f"{'='*60}\n")
# ── Engineering Validation ─────────────────────────────────
print(f"\n{'='*60}")
print(f"  ENGINEERING VALIDATION CHECKS")
print(f"{'='*60}\n")

eng_results = [
    check_mechanical_sequence(activities, relationships),
    check_energy_dependencies(activities, relationships),
]

for r in eng_results:
    icon = "✅" if r['status'] == "PASS" else "❌"
    print(f"  {icon} {r['check']}")
    print(f"     Status     : {r['status']}")
    print(f"     Violations : {r['violations']} / {r['total']}")
    if r['details']:
        for v in r['details']:
            if 'task_code' in v:
                print(f"       ↳ [{v['task_code']}] {v['issue']}")
            else:
                print(f"       ↳ [{v['pred_code']}→{v['succ_code']}] {v['issue']}")
    else:
        print(f"     ✔ No violations found")
    print()

print(f"{'='*60}\n")
