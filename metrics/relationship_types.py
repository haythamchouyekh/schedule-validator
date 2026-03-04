# metrics/relationship_types.py
# Metric #4: Relationship Types (SF relationships)
# Start-to-Finish (SF) relationships are considered bad practice
# They create confusing logic and are almost never justified
# DCMA threshold: 0% SF relationships allowed
# Also flags: SS and FF used excessively (threshold: max 10% of total)

SS_FF_THRESHOLD_PCT = 10  # max 10% SS or FF combined

def check_relationship_types(activities, relationships):
    """
    Checks all relationships for SF usage and excessive SS/FF usage.
    Returns a result dict with status, violations, and summary.
    """
    sf_violations  = []
    ssff_list      = []

    for rel in relationships:
        pred = activities.get(rel.pred_task_id)
        succ = activities.get(rel.succ_task_id)

        pred_code = pred.task_code if pred else rel.pred_task_id
        succ_code = succ.task_code if succ else rel.succ_task_id

        # SF is always flagged
        if rel.pred_type == "PR_SF":
            sf_violations.append({
                "pred_code" : pred_code,
                "succ_code" : succ_code,
                "rel_type"  : "SF",
                "issue"     : f"Start-to-Finish (SF) relationship: {pred_code} → {succ_code}"
            })

        # SS and FF are tracked for percentage check
        if rel.pred_type in ("PR_SS", "PR_FF"):
            ssff_list.append({
                "pred_code" : pred_code,
                "succ_code" : succ_code,
                "rel_type"  : rel.pred_type.replace("PR_", ""),
                "issue"     : (f"{rel.pred_type.replace('PR_','')} relationship: "
                               f"{pred_code} → {succ_code}")
            })

    total_rels   = len(relationships)
    ssff_pct     = round((len(ssff_list) / total_rels) * 100, 1) if total_rels > 0 else 0
    ssff_fail    = ssff_pct > SS_FF_THRESHOLD_PCT

    all_violations = sf_violations + (ssff_list if ssff_fail else [])
    count          = len(sf_violations)  # primary violation = SF
    passed         = len(sf_violations) == 0 and not ssff_fail

    return {
        "metric"     : "Metric #4 - Relationship Types",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total_rels,
        "violations" : count,
        "percentage" : round((count / total_rels) * 100, 1) if total_rels > 0 else 0,
        "threshold"  : "0% SF | max 10% SS+FF",
        "sf_count"   : len(sf_violations),
        "ssff_count" : len(ssff_list),
        "ssff_pct"   : ssff_pct,
        "details"    : all_violations
    }
