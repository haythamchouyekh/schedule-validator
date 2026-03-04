# metrics/remaining_metrics.py
# Metrics #11-14: Logic Density, BEI, Summary Tasks, CPLI

from datetime import datetime

def _parse_date(d):
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(str(d).strip(), fmt)
        except:
            pass
    return None


# ── Metric #11: Logic Density ─────────────────────────────
# DCMA definition: Total Relationships / Total Activities ≥ 1.0
# Also flags activities with NO logic at all

def check_logic_density(activities):
    total_acts = len([a for a in activities.values()
                      if a.task_type not in ("TT_Mile","TT_WBS","TT_LOE")])
    total_rels = sum(len(a.predecessors) for a in activities.values())

    # Density ratio
    density_ratio = round(total_rels / total_acts, 2) if total_acts > 0 else 0
    passed_ratio  = density_ratio >= 1.0

    # Also flag activities with zero logic
    violations = []
    for act in activities.values():
        if act.task_type in ("TT_Mile", "TT_WBS", "TT_LOE"):
            continue
        if len(act.predecessors) == 0 and len(act.successors) == 0:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "Activity has NO logic (zero predecessors and successors)"
            })

    passed = passed_ratio and len(violations) == 0

    return {
        "metric"        : "Metric #11 - Logic Density",
        "status"        : "PASS" if passed else "FAIL",
        "total"         : total_acts,
        "violations"    : len(violations),
        "percentage"    : round((len(violations) / total_acts) * 100, 1) if total_acts > 0 else 0,
        "threshold"     : "Ratio ≥ 1.0 relationships/activity",
        "density_ratio" : density_ratio,
        "details"       : violations
    }


# ── Metric #12: BEI (Baseline Execution Index) ────────────
# DCMA formula: BEI = Completed Activities / Planned Activities by Data Date
# Threshold: BEI ≥ 0.95
# Falls back to status-check if no data date available

def check_missed_activities(activities, data_date_str=None):
    violations = []

    if data_date_str:
        # ── Full BEI calculation ──
        data_date = _parse_date(data_date_str)

        if data_date:
            planned   = []
            completed = []

            for act in activities.values():
                if act.task_type in ("TT_Mile", "TT_WBS", "TT_LOE"):
                    continue
                finish_dt = _parse_date(act.finish)
                if finish_dt and finish_dt <= data_date:
                    planned.append(act)
                    if act.status_code == "TK_Complete":
                        completed.append(act)

            total    = len(planned)
            done     = len(completed)
            BEI      = round(done / total, 3) if total > 0 else 1.0
            passed   = BEI >= 0.95
            not_done = [a for a in planned if a not in completed]

            for act in not_done:
                violations.append({
                    "task_code" : act.task_code,
                    "task_name" : act.task_name,
                    "issue"     : f"Planned to complete by data date but not finished"
                })

            return {
                "metric"     : "Metric #12 - BEI (Baseline Execution Index)",
                "status"     : "PASS" if passed else "FAIL",
                "total"      : total,
                "violations" : len(violations),
                "percentage" : round((len(violations) / total) * 100, 1) if total > 0 else 0,
                "threshold"  : "BEI ≥ 0.95",
                "bei_value"  : BEI,
                "details"    : violations
            }

    # ── Fallback: status consistency check ──
    for act in activities.values():
        if act.task_type in ("TT_Mile", "TT_WBS", "TT_LOE"):
            continue
        if act.status_code == "TK_Active" and not act.act_start:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "Active but no actual start date recorded"
            })
        if act.status_code == "TK_Complete" and not act.act_finish:
            violations.append({
                "task_code" : act.task_code,
                "task_name" : act.task_name,
                "issue"     : "Complete but no actual finish date recorded"
            })

    total      = len(activities)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0

    return {
        "metric"     : "Metric #12 - BEI (Status Consistency Check)",
        "status"     : "PASS" if count == 0 else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0 status inconsistencies",
        "bei_value"  : None,
        "details"    : violations
    }


# ── Metric #13: Summary Tasks Used in Logic ───────────────
# WBS/LOE tasks should never drive or be driven by logic

def check_summary_tasks(activities):
    violations = []
    for act in activities.values():
        if act.task_type in ("TT_WBS", "TT_LOE"):
            if len(act.predecessors) > 0 or len(act.successors) > 0:
                violations.append({
                    "task_code" : act.task_code,
                    "task_name" : act.task_name,
                    "issue"     : (f"Summary/LOE task has logic: "
                                   f"{len(act.predecessors)} predecessors, "
                                   f"{len(act.successors)} successors")
                })

    total      = len(activities)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0

    return {
        "metric"     : "Metric #13 - Summary Tasks in Logic",
        "status"     : "PASS" if count == 0 else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0%",
        "details"    : violations
    }


# ── Metric #14: CPLI (Critical Path Length Index) ─────────
# DCMA formula: CPLI = (CPL + TF) / CPL
# Where:
#   CPL = sum of remaining durations of all critical activities (float = 0)
#   TF  = total float of the last critical activity (end of critical path)
# Threshold: CPLI ≥ 0.95

def check_critical_path(activities):
    critical = [a for a in activities.values()
                if a.total_float == 0
                and a.task_type not in ("TT_Mile", "TT_WBS", "TT_LOE")]

    if not critical:
        return {
            "metric"     : "Metric #14 - CPLI (Critical Path Length Index)",
            "status"     : "PASS",
            "total"      : len(activities),
            "violations" : 0,
            "percentage" : 0,
            "threshold"  : "CPLI ≥ 0.95",
            "cpli_value" : 1.0,
            "details"    : []
        }

    # CPL = total remaining duration on critical path
    CPL = sum(a.remaining_dur for a in critical)

    # TF = float of the last activity on critical path (end milestone proxy)
    # Use minimum float among critical activities (most constrained)
    TF  = min(a.total_float for a in critical)

    CPLI   = round((CPL + TF) / CPL, 3) if CPL > 0 else 0.0
    passed = CPLI >= 0.95

    violations = []
    if not passed:
        violations.append({
            "task_code" : "SCHEDULE",
            "task_name" : "Critical Path",
            "issue"     : (f"CPLI = {CPLI} — below 0.95 threshold. "
                           f"CPL = {CPL}h, TF = {TF}h. "
                           f"Critical path has {len(critical)} activities.")
        })

    return {
        "metric"     : "Metric #14 - CPLI (Critical Path Length Index)",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : len(activities),
        "violations" : len(violations),
        "percentage" : round((len(critical) / len(activities)) * 100, 1),
        "threshold"  : "CPLI ≥ 0.95",
        "cpli_value" : CPLI,
        "cp_count"   : len(critical),
        "details"    : violations
    }
