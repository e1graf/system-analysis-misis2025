import json
from typing import Any, List, Tuple


def flatten_ranking(ranking: List[Any]) -> List[str]:
    result = []
    for item in ranking:
        if isinstance(item, list):
            result.extend([str(x) for x in item])
        else:
            result.append(str(item))
    return result


def get_all_objects(ranking_a: List[Any], ranking_b: List[Any]) -> List[str]:
    objects_a = set(flatten_ranking(ranking_a))
    objects_b = set(flatten_ranking(ranking_b))
    all_objects = sorted(
        list(objects_a | objects_b),
        key=lambda x: (len(str(x)), str(x))
    )
    return all_objects


def build_relation_matrix(ranking: List[Any], objects: List[str]) -> List[List[int]]:
    n = len(objects)
    obj_to_idx = {obj: i for i, obj in enumerate(objects)}
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    positions = {}
    pos = 0
    
    for item in ranking:
        if isinstance(item, list):
            cluster_objs = [str(o) for o in item if str(o) in obj_to_idx]
            for obj in cluster_objs:
                positions[obj] = pos
            pos += 1
        else:
            obj = str(item)
            if obj in obj_to_idx:
                positions[obj] = pos
            pos += 1
    
    for i in range(n):
        matrix[i][i] = 1
    
    for i in range(n):
        for j in range(n):
            obj_i = objects[i]
            obj_j = objects[j]
            
            if obj_i not in positions or obj_j not in positions:
                continue
            
            if positions[obj_i] <= positions[obj_j]:
                matrix[i][j] = 1
    
    return matrix


def transpose(matrix: List[List[int]]) -> List[List[int]]:
    n = len(matrix)
    return [[matrix[j][i] for j in range(n)] for i in range(n)]


def logical_and(a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
    n = len(a)
    return [
        [1 if (a[i][j] == 1 and b[i][j] == 1) else 0 for j in range(n)]
        for i in range(n)
    ]


def logical_or(a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
    n = len(a)
    return [
        [1 if (a[i][j] == 1 or b[i][j] == 1) else 0 for j in range(n)]
        for i in range(n)
    ]


def find_contradictions(ya: List[List[int]], yb: List[List[int]]) -> List[Tuple[int, int]]:
    ya_t = transpose(ya)
    yb_t = transpose(yb)
    
    part1 = logical_and(ya, yb_t)
    part2 = logical_and(ya_t, yb)
    p = logical_or(part1, part2)
    
    n = len(ya)
    contradictions = []
    seen = set()
    
    for i in range(n):
        for j in range(n):
            if i == j or p[i][j] == 0:
                continue
            
            condition1 = (ya[i][j] == 1 and ya[j][i] == 0 and 
                         yb[i][j] == 0 and yb[j][i] == 1)
            condition2 = (ya[i][j] == 0 and ya[j][i] == 1 and 
                         yb[i][j] == 1 and yb[j][i] == 0)
            
            if condition1 or condition2:
                pair = tuple(sorted([i, j]))
                if pair not in seen:
                    seen.add(pair)
                    contradictions.append((i, j))
    
    return contradictions


def warshall_closure(matrix: List[List[int]]) -> List[List[int]]:
    n = len(matrix)
    result = [row[:] for row in matrix]
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if result[i][k] == 1 and result[k][j] == 1:
                    result[i][j] = 1
    
    return result


def find_clusters(equivalence: List[List[int]], objects: List[str]) -> List[List[str]]:
    n = len(objects)
    visited = [False] * n
    clusters = []
    
    for i in range(n):
        if visited[i]:
            continue
        
        cluster = []
        stack = [i]
        visited[i] = True
        
        while stack:
            node = stack.pop()
            cluster.append(objects[node])
            
            for j in range(n):
                if not visited[j] and equivalence[node][j] == 1:
                    visited[j] = True
                    stack.append(j)
        
        clusters.append(cluster)
    
    return clusters


def compare_clusters(
    cluster_a: List[str],
    cluster_b: List[str],
    c_matrix: List[List[int]],
    objects: List[str]
) -> int:
    if cluster_a == cluster_b:
        return 0
    
    obj_to_idx = {obj: i for i, obj in enumerate(objects)}
    a_better = 0
    b_better = 0
    
    for obj_a in cluster_a:
        for obj_b in cluster_b:
            if obj_a not in obj_to_idx or obj_b not in obj_to_idx:
                continue
            
            idx_a = obj_to_idx[obj_a]
            idx_b = obj_to_idx[obj_b]
            
            if c_matrix[idx_a][idx_b] == 1 and c_matrix[idx_b][idx_a] == 0:
                a_better += 1
            elif c_matrix[idx_a][idx_b] == 0 and c_matrix[idx_b][idx_a] == 1:
                b_better += 1
    
    if a_better > 0 and b_better == 0:
        return -1
    elif b_better > 0 and a_better == 0:
        return 1
    else:
        return 0


def order_clusters(
    clusters: List[List[str]],
    c_matrix: List[List[int]],
    objects: List[str]
) -> List[List[str]]:
    if len(clusters) <= 1:
        return clusters
    
    n = len(clusters)
    cluster_graph = [[0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j:
                cmp = compare_clusters(clusters[i], clusters[j], c_matrix, objects)
                if cmp < 0:
                    cluster_graph[i][j] = 1
    
    in_degree = [sum(cluster_graph[j][i] for j in range(n)) for i in range(n)]
    
    result = []
    used = [False] * n
    queue = [i for i in range(n) if in_degree[i] == 0]
    
    while queue:
        node = queue.pop(0)
        if used[node]:
            continue
        
        used[node] = True
        result.append(clusters[node])
        
        for j in range(n):
            if cluster_graph[node][j] == 1:
                in_degree[j] -= 1
                if in_degree[j] == 0 and not used[j]:
                    queue.append(j)
    
    for i in range(n):
        if not used[i]:
            result.append(clusters[i])
    
    return result


def main(s1: str, s2: str) -> str:
    ranking_a = json.loads(s1)
    ranking_b = json.loads(s2)
    
    objects = get_all_objects(ranking_a, ranking_b)
    
    ya = build_relation_matrix(ranking_a, objects)
    yb = build_relation_matrix(ranking_b, objects)
    
    contradictions_indices = find_contradictions(ya, yb)
    contradictions = [[objects[i], objects[j]] for i, j in contradictions_indices]
    
    c = logical_and(ya, yb)
    
    for i, j in contradictions_indices:
        c[i][j] = 1
        c[j][i] = 1
    
    c_t = transpose(c)
    e = logical_and(c, c_t)
    e_star = warshall_closure(e)
    
    clusters = find_clusters(e_star, objects)
    ordered_clusters = order_clusters(clusters, c, objects)
    
    result = []
    for cluster in ordered_clusters:
        if len(cluster) == 1:
            result.append(cluster[0])
        else:
            result.append(sorted(cluster))
    
    return json.dumps(result)
