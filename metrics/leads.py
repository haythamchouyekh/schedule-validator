# metrics/leads.py
# Metric #2: Leads (Negative Lags)
# A "lead" is a relationship with a negative lag value
# Leads are forbidden in good scheduling — they imply an activity
# starts BEFORE its predecessor finishes, which is unrealistic
# DCMA threshold: 0% leads allowed

def check_leads(activities, relationships):
    """
    Checks all relationships for negative lag values (leads).
    Returns a result dict with status, violations, and summary.
    """
    violations = []

    for rel in relationships:
        if rel.lag < 0:
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
                "rel_type"  : rel.pred_type,
                "issue"     : f"Negative lag of {rel.lag}h between {pred_code} → {succ_code}"
            })

    total_rels = len(relationships)
    count      = len(violations)
    percentage = round((count / total_rels) * 100, 1) if total_rels > 0 else 0
    passed     = count == 0

    return {
        "metric"     : "Metric #2 - Leads (Negative Lags)",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total_rels,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0%",
        "details"    : violations
    }
