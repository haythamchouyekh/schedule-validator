# metrics/open_ends.py
# Metric #1: Open Ends
# An activity is an "open end" if it has no predecessors OR no successors
# Exception: milestones at project start/end are allowed to have one open end
# DCMA threshold: 0% open ends (any open end is a violation)

def check_open_ends(activities):
    """
    Checks all activities for open ends.
    Returns a result dict with status, violations, and summary.
    """
    violations = []

    for act in activities.values():
        has_no_pred = len(act.predecessors) == 0
        has_no_succ = len(act.successors) == 0

        # Both ends open = dangling activity (worst case)
        if has_no_pred and has_no_succ:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "No predecessors AND no successors (fully isolated)"
            })

        # No predecessor only (except the very first milestone)
        elif has_no_pred:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "No predecessors (open start)"
            })

        # No successor only (except the very last milestone)
        elif has_no_succ:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "No successors (open finish)"
            })

    total      = len(activities)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = count == 0

    return {
        "metric"     : "Metric #1 - Open Ends",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0%",
        "details"    : violations
    }
