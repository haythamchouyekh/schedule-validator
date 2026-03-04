# metrics/high_float.py
# Metric #6: High Float
# DCMA threshold: max 5% of activities may have high float > 44 days (352h)

FLOAT_THRESHOLD_HOURS = 352  # 44 days × 8h
ACTIVITY_PCT_LIMIT    = 5    # max 5% of activities

def check_high_float(activities):
    violations = []
    for act in activities.values():
        if act.task_type in ("TT_Mile", "TT_WBS", "TT_LOE"):
            continue
        if act.total_float > FLOAT_THRESHOLD_HOURS:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : (f"Excessive total float: "
                               f"{round(act.total_float, 1)}h "
                               f"({round(act.total_float/8, 1)} days)")
            })

    # Deduplicate by task_code
    seen   = set()
    unique = []
    for v in violations:
        if v['task_code'] not in seen:
            seen.add(v['task_code'])
            unique.append(v)
    violations = unique

    total      = len([a for a in activities.values()
                      if a.task_type not in ("TT_Mile","TT_WBS","TT_LOE")])
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = percentage <= ACTIVITY_PCT_LIMIT

    return {
        "metric"     : "Metric #6 - High Float",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : f"Max {ACTIVITY_PCT_LIMIT}% with float > {FLOAT_THRESHOLD_HOURS}h",
        "details"    : violations
    }


