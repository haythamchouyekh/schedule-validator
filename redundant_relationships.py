# metrics/redundant_relationships.py
# Redundancy Detection: If A → B → C and A → C exist,
# then A → C is redundant and should be removed
# This is also known as "Transitive Closure" detection

def _build_reachability(activities):
    """
    For each activity, compute all activities reachable through successors
    using Depth-First Search (DFS).
    Returns dict: task_id → set of reachable task_ids (excluding direct successors)
    """
    # Build adjacency: task_id → list of direct successor task_ids
    adj = {tid: set() for tid in activities}
    for act in activities.values():
        for rel in act.successors:
            if rel.succ_task_id in activities:
                adj[act.task_id].add(rel.succ_task_id)

    # DFS to get ALL reachable nodes from a given start
    def dfs(start, visited=None):
        if visited is None:
            visited = set()
        for neighbor in adj.get(start, []):
            if neighbor not in visited:
                visited.add(neighbor)
                dfs(neighbor, visited)
        return visited

    reachable = {}
    for tid in activities:
        reachable[tid] = dfs(tid)

    return adj, reachable


def check_redundant_relationships(activities, relationships):
    """
    Detects redundant relationships where a direct link A → C exists
    but C is already reachable from A through another path (A → B → ... → C).
    """
    adj, reachable = _build_reachability(activities)

    violations = []

    for rel in relationships:
        pred_id = rel.pred_task_id
        succ_id = rel.succ_task_id

        if pred_id not in activities or succ_id not in activities:
            continue

        # Check: is succ_id reachable from pred_id WITHOUT using this direct link?
        # Temporarily remove the direct link and check reachability
        # Strategy: check if succ_id appears in reachable paths of
        # ANY other direct successor of pred_id

        other_successors = [s for s in adj.get(pred_id, []) if s != succ_id]

        indirect_reachable = set()
        for other_succ in other_successors:
            indirect_reachable.add(other_succ)
            indirect_reachable.update(reachable.get(other_succ, set()))

        if succ_id in indirect_reachable:
            pred_act = activities[pred_id]
            succ_act = activities[succ_id]

            # Find the intermediate path for the message
            path_node = None
            for other_succ in other_successors:
                if other_succ == succ_id or succ_id in reachable.get(other_succ, set()):
                    path_node = activities.get(other_succ)
                    break

            path_str = f" via {path_node.task_code}" if path_node else ""

            violations.append({
                "pred_code"  : pred_act.task_code,
                "pred_name"  : pred_act.task_name,
                "succ_code"  : succ_act.task_code,
                "succ_name"  : succ_act.task_name,
                "rel_type"   : rel.pred_type.replace("PR_", ""),
                "issue"      : (f"Redundant link: {pred_act.task_code} → {succ_act.task_code} "
                                f"is unnecessary{path_str}. "
                                f"Remove this relationship.")
            })

    total      = len(relationships)
    count      = len(violations)
    percentage = round((count / total) * 100, 1) if total > 0 else 0
    passed     = count == 0

    return {
        "metric"     : "Metric #15 - Redundant Relationships",
        "status"     : "PASS" if passed else "FAIL",
        "total"      : total,
        "violations" : count,
        "percentage" : percentage,
        "threshold"  : "0% redundant relationships",
        "details"    : violations
    }
