from math import e, log, log2
from typing import Dict, List, Tuple


def mark_reachable(src: int, node: int, graph: Dict[int, List[int]], reach: List[List[bool]]) -> None:
    for nxt in graph.get(node, []):
        if not reach[src - 1][nxt - 1]:
            reach[src - 1][nxt - 1] = True
            mark_reachable(src, nxt, graph, reach)


def build_relations(edges_text: str) -> Tuple[
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
]:
    edges = [tuple(map(int, line.split(","))) for line in edges_text.splitlines() if line.strip()]
    n = max(max(u, v) for u, v in edges)

    direct_parent = [[False] * n for _ in range(n)]
    graph: Dict[int, List[int]] = {i: [] for i in range(1, n + 1)}
    parent_of: Dict[int, int] = {}

    for u, v in edges:
        direct_parent[u - 1][v - 1] = True
        graph[u].append(v)
        parent_of[v] = u

    direct_child = [[direct_parent[j][i] for j in range(n)] for i in range(n)]

    reach = [[False] * n for _ in range(n)]
    for v in range(1, n + 1):
        mark_reachable(v, v, graph, reach)

    indirect_parent = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and reach[i][j] and not direct_parent[i][j]:
                indirect_parent[i][j] = True

    indirect_child = [[indirect_parent[j][i] for j in range(n)] for i in range(n)]

    co_level = [[False] * n for _ in range(n)]
    for i in range(1, n + 1):
        pi = parent_of.get(i)
        if pi is None:
            continue
        for j in range(1, n + 1):
            if i != j and parent_of.get(j) == pi:
                co_level[i - 1][j - 1] = True

    return direct_parent, direct_child, indirect_parent, indirect_child, co_level


def compute_entropy(edges_text: str) -> Tuple[float, float]:
    rels = build_relations(edges_text)
    n = len(rels[0])
    k = len(rels)

    total = 0.0
    denom = (n - 1)

    for i in range(n):
        for r in rels:
            cnt = sum(r[i])
            if cnt:
                p = cnt / denom
                total += -p * log2(p)

    ref = (1 / (e * log(2))) * n * k
    normalized = total / ref

    return round(total, 1), round(normalized, 1)


if __name__ == "__main__":
    s = "1,2\n1,3\n3,4\n3,5"
    H, h = compute_entropy(s)

    print("Энтропия:", H)
    print("Нормированная сложность:", h)