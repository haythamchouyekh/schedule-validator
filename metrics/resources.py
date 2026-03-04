# metrics/resources.py
# Metric #10: Missing Resources
# All non-milestone activities should have resources assigned
# We check via task_type — in a real XER, TASKRSRC table would be used
# For now we flag activities with no calendar or no WBS as proxy

def check_resources(activities):
    violations = []
    for act in activities.values():
        if act.task_type == "TT_Mile":
            continue
        if not act.wbs_id or not act.calendar_id:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : (f"Missing {'WBS' if not act.wbs_id else 'Calendar'} "
                               f"assignment")
            })

    total      = len(activities)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = count == 0

    return {
        "metric"     : "Metric #10 - Missing WBS/Calendar",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0%",
        "details"    : violations
    }
