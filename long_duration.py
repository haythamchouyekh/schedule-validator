# metrics/long_duration.py
# Metric #8: Long Activity Durations
# DCMA threshold: max duration = 44 working days (352h)
# Excludes: milestones, WBS summary tasks, LOE tasks

DURATION_THRESHOLD_HOURS = 352  # 44 days × 8h
EXCLUDED_TYPES = ("TT_Mile", "TT_WBS", "TT_LOE")

def check_long_duration(activities):
    violations = []
    for act in activities.values():
        if act.task_type in EXCLUDED_TYPES:
            continue
        if act.duration > DURATION_THRESHOLD_HOURS:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : (f"Duration too long: "
                               f"{act.duration}h "
                               f"({round(act.duration/8, 1)} days) "
                               f"— exceeds {DURATION_THRESHOLD_HOURS}h limit")
            })

    total      = len([a for a in activities.values()
                      if a.task_type not in EXCLUDED_TYPES])
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = percentage == 0

    return {
        "metric"     : "Metric #8 - Long Activity Durations",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : f"Max {DURATION_THRESHOLD_HOURS}h (44 days)",
        "details"    : violations
    }
