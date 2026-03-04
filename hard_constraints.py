# metrics/hard_constraints.py
# Metric #5: Hard Constraints
# Hard constraints override CPM logic and make schedules unrealistic
# Allowed: CS_MSO (Must Start On), CS_MFO (Must Finish On) only when justified
# Forbidden: CS_ALAP, CS_FNLT, CS_SNLT, CS_FNET, CS_SNET used excessively
# DCMA threshold: max 5% of activities may have hard constraints

HARD_CONSTRAINTS = ["CS_MSO", "CS_MFO", "CS_ALAP", "CS_FNLT",
                    "CS_SNLT", "CS_FNET", "CS_SNET"]
THRESHOLD_PCT = 5

def check_hard_constraints(activities):
    violations = []
    for act in activities.values():
        if act.constraint in HARD_CONSTRAINTS or act.constraint2 in HARD_CONSTRAINTS:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : f"Hard constraint: {act.constraint or act.constraint2}"
            })

    total      = len(activities)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = percentage <= THRESHOLD_PCT

    return {
        "metric"     : "Metric #5 - Hard Constraints",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : f"Max {THRESHOLD_PCT}%",
        "details"    : violations
    }
