# metrics/lags.py
# Metric #3: Lags (Excessive Positive Lags)
# A lag is a delay imposed on a relationship between two activities
# Excessive lags hide float and make the schedule unrealistic
# DCMA threshold: max 5% of relationships may have lags
# Common rule: any lag > 2 working days (16h) is flagged

LAG_THRESHOLD_HOURS = 16  # 2 working days × 8h

def check_lags(activities, relationships):
    """
    Checks all relationships for excessive positive lag values.
    Returns a result dict with status, violations, and summary.
    """
    violations = []

    for rel in relationships:
        if rel.lag > LAG_THRESHOLD_HOURS:
            pred = activities.get(rel.pred_task_id)
            succ = activities.get(rel.succ_task_id)

            pred_code = pred.task_code if pred else rel.pred_task_id
            succ_code = succ.task_code if succ else rel.succ_task_id
            pred_name = pred.task_name if pred else "Unknown"
            succ_name = succ.task_name if succ else "Unknown"

            violations.append({
                "pred_code" : pred_code,
                "pred_name" : pred_name,
                "succ_code" : succ_code,
                "succ_name" : succ_name,
                "lag"       : rel.lag,
                "lag_days"  : round(rel.lag / 8, 1),
                "rel_type"  : rel.pred_type,
                "issue"     : (f"Excessive lag of {rel.lag}h "
                               f"({round(rel.lag/8,1)} days) "
                               f"on {pred_code} → {succ_code}")
            })

    total_rels = len(relationships)
    count      = len(violations)
    percentage = round((count / total_rels) * 100, 1) if total_rels > 0 else 0
    passed     = percentage == 0

    return {
        "metric"     : "Metric #3 - Lags (Excessive Positive Lags)",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total_rels,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0% (lag > 16h flagged)",
        "details"    : violations
    }
