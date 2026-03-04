# engineering/mechanical_checks.py
# Engineering Validation #1: Mechanical Sequence Checks
# Verifies that activities follow realistic mechanical construction logic
# Rules based on EPC industry standards:
#   - Foundation must come before installation
#   - Installation must come before testing
#   - Testing must come before commissioning
#   - Commissioning must come before handover

# Keywords that identify activity types from their names
FOUNDATION_KW     = ["foundation", "civil", "concrete", "excavat", "grout"]
INSTALLATION_KW   = ["install", "erect", "setting", "assembly", "assembl", "mount"]
TESTING_KW        = ["test", "inspect", "check", "loop", "verify", "hydro"]
COMMISSIONING_KW  = ["commission", "pre-comm", "precomm", "startup", "start-up"]
HANDOVER_KW       = ["handover", "hand-over", "close", "turnover", "transfer"]

def classify_activity(name):
    name_lower = name.lower()
    if any(k in name_lower for k in HANDOVER_KW):
        return "HANDOVER"
    if any(k in name_lower for k in COMMISSIONING_KW):
        return "COMMISSIONING"
    if any(k in name_lower for k in TESTING_KW):
        return "TESTING"
    if any(k in name_lower for k in INSTALLATION_KW):
        return "INSTALLATION"
    if any(k in name_lower for k in FOUNDATION_KW):
        return "FOUNDATION"
    return "OTHER"

# Valid sequence order
SEQUENCE_ORDER = {
    "FOUNDATION"    : 1,
    "INSTALLATION"  : 2,
    "TESTING"       : 3,
    "COMMISSIONING" : 4,
    "HANDOVER"      : 5,
    "OTHER"         : 0
}

def check_mechanical_sequence(activities, relationships):
    """
    Checks that mechanical activities follow the correct construction sequence.
    Flags relationships where a successor has a LOWER sequence rank than its predecessor.
    """
    violations = []

    for rel in relationships:
        pred = activities.get(rel.pred_task_id)
        succ = activities.get(rel.succ_task_id)

        if not pred or not succ:
            continue

        pred_class = classify_activity(pred.task_name)
        succ_class = classify_activity(succ.task_name)

        # Skip if either is unclassified
        if pred_class == "OTHER" or succ_class == "OTHER":
            continue

        pred_rank = SEQUENCE_ORDER[pred_class]
        succ_rank = SEQUENCE_ORDER[succ_class]

        # Successor should have equal or higher rank than predecessor
        if succ_rank < pred_rank:
            violations.append({
                "pred_code"  : pred.task_code,
                "pred_name"  : pred.task_name,
                "pred_class" : pred_class,
                "succ_code"  : succ.task_code,
                "succ_name"  : succ.task_name,
                "succ_class" : succ_class,
                "issue"      : (f"Wrong sequence: {pred_class} ({pred.task_code}) "
                                f"→ {succ_class} ({succ.task_code}) "
                                f"[{succ_class} should come BEFORE {pred_class}]")
            })

    total  = len(relationships)
    count  = len(violations)
    passed = count == 0

    return {
        "check"      : "Engineering Check #1 - Mechanical Sequence",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "details"    : violations
    }
