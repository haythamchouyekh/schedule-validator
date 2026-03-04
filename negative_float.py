# metrics/negative_float.py
# Metric #7: Negative Float
# Negative float means the activity is behind schedule
# Any negative float is a critical warning
# DCMA threshold: 0% negative float allowed

def check_negative_float(activities):
    violations = []
    for act in activities.values():
        if act.total_float < 0:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : (f"Negative total float: "
                               f"{act.total_float}h "
                               f"({round(act.total_float/8,1)} days)")
            })

    total      = len(activities)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = count == 0

    return {
        "metric"     : "Metric #7 - Negative Float",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0%",
        "details"    : violations
    }
