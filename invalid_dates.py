# metrics/invalid_dates.py
# Metric #9: Invalid or Missing Dates
# All activities must have valid early start and early finish dates
# Missing dates indicate incomplete schedule logic

from datetime import datetime

def parse_date(d):
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(d.strip(), fmt)
        except:
            pass
    return None

def check_invalid_dates(activities):
    violations = []
    for act in activities.values():
        start  = parse_date(act.start)
        finish = parse_date(act.finish)

        if not start and not finish:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "Missing both start and finish dates"
            })
        elif not start:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "Missing start date"
            })
        elif not finish:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "Missing finish date"
            })
        elif finish < start:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : f"Finish date before start date: {act.start} → {act.finish}"
            })

    total      = len(activities)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = count == 0

    return {
        "metric"     : "Metric #9 - Invalid/Missing Dates",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0%",
        "details"    : violations
    }
