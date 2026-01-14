from typing import Dict, List, Tuple

def compute_reachability(node: int, graph: Dict[int, List[int]], visited: set) -> set:
    """DFS to find all nodes reachable from a given node."""
    reachable = set()
    stack = [node]
    
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        reachable.add(current)
        stack.extend(graph.get(current, []))
    
    return reachable

def transpose_matrix(matrix: List[List[bool]]) -> List[List[bool]]:
    """Transpose a boolean matrix."""
    n = len(matrix)
    return [[matrix[j][i] for j in range(n)] for i in range(n)]

def solve(edges_text: str) -> Tuple[
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
]:
    edges = [tuple(map(int, line.split(","))) for line in edges_text.splitlines() if line.strip()]
    n = max(max(u, v) for u, v in edges)
    
    # Build adjacency list and parent mapping
    graph: Dict[int, List[int]] = {i: [] for i in range(1, n + 1)}
    parent_of: Dict[int, int] = {}
    
    for u, v in edges:
        graph[u].append(v)
        parent_of[v] = u
    
    # Direct parent matrix (u→v means u is direct parent of v)
    direct_parent = [[False] * n for _ in range(n)]
    for u, v in edges:
        direct_parent[u - 1][v - 1] = True
    
    direct_child = transpose_matrix(direct_parent)
    
    # Compute full reachability
    reachability = [[False] * n for _ in range(n)]
    for node in range(1, n + 1):
        reachable = compute_reachability(node, graph, set())
        for target in reachable:
            reachability[node - 1][target - 1] = True
    
    # Indirect parent = reachable but not direct
    indirect_parent = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and reachability[i][j] and not direct_parent[i][j]:
                indirect_parent[i][j] = True
    
    indirect_child = transpose_matrix(indirect_parent)
    
    # Co-level = share the same parent
    co_level = [[False] * n for _ in range(n)]
    for i in range(1, n + 1):
        parent_i = parent_of.get(i)
        if parent_i is None:
            continue
        for j in range(1, n + 1):
            if i != j and parent_of.get(j) == parent_i:
                co_level[i - 1][j - 1] = True
    
    return direct_parent, direct_child, indirect_parent, indirect_child, co_level

def print_matrix(title: str, matrix: List[List[bool]]) -> None:
    print(f"{title}:")
    for row in matrix:
        print(" ".join("1" if cell else "0" for cell in row))
    print()

if __name__ == "__main__":
    edges_text = "1,2\n1,3\n3,4\n3,5"
    dir_parent, dir_child, indir_parent, indir_child, co_parent = solve(edges_text)
    
    print_matrix("Непосредственное управление", dir_parent)
    print_matrix("Непосредственное подчинение", dir_child)
    print_matrix("Опосредованное управление", indir_parent)
    print_matrix("Опосредованное подчинение", indir_child)
    print_matrix("Соподчинение на одном уровне", co_parent)