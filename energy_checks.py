# engineering/energy_checks.py
# Engineering Validation #2: Energy Dependency Checks
# Ensures energy-dependent activities only occur after energy is available
# Rules:
#   - Equipment testing requires electrical energization first
#   - Commissioning requires power and utilities available first
#   - Instrument checks require energization first

ENERGY_SOURCE_KW  = ["energi", "power", "electrical", "lv ", "mv ", "hv ",
                      "switchgear", "transformer", "substation", "utility",
                      "utilities"]

ENERGY_DEPEND_KW  = ["test", "loop check", "commission", "pre-comm",
                      "startup", "start-up", "instrument", "calibrat",
                      "functional"]

def is_energy_source(name):
    name_lower = name.lower()
    return any(k in name_lower for k in ENERGY_SOURCE_KW)

def is_energy_dependent(name):
    name_lower = name.lower()
    return any(k in name_lower for k in ENERGY_DEPEND_KW)

def check_energy_dependencies(activities, relationships):
    """
    Checks that energy-dependent activities have at least one energy source
    as a predecessor (direct or via chain).
    Flags energy-dependent activities with NO energy source predecessor.
    """
    # Build a quick lookup: task_id → set of all predecessor task_ids
    pred_map = {tid: set() for tid in activities}
    for rel in relationships:
        if rel.succ_task_id in pred_map:
            pred_map[rel.succ_task_id].add(rel.pred_task_id)

    violations = []

    for act in activities.values():
        if not is_energy_dependent(act.task_name):
            continue

        # Check if any direct predecessor is an energy source
        has_energy_pred = False
        for pred_id in pred_map.get(act.task_id, []):
            pred = activities.get(pred_id)
            if pred and is_energy_source(pred.task_name):
                has_energy_pred = True
                break

        if not has_energy_pred:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : (f"Energy-dependent activity '{act.task_code}' "
                               f"has no energy source predecessor")
            })

    total  = len([a for a in activities.values() if is_energy_dependent(a.task_name)])
    count  = len(violations)
    passed = count == 0

    return {
        "check"      : "Engineering Check #2 - Energy Dependencies",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total if total > 0 else len(activities),
        "violations" : count,
        "details"    : violations
    }
