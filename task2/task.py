from math import e, log2
import numpy as np
from collections import defaultdict


def dfs(graph, edge, seen=None, path=None):
    if seen is None:
        seen = []
    if path is None:
        path = [edge]
    
    seen.append(edge)
    paths = []
    
    for e in graph[edge]:
        if e not in seen:
            t_path = path + [e]
            paths.append(tuple(t_path))
            paths.extend(dfs(graph, e, seen[:], t_path))
    
    return paths


def task1(s: str) -> tuple[list[list[bool]], list[list[bool]], list[list[bool]], list[list[bool]], list[list[bool]]]:
    pairs = [item.split(',') for item in s.split('\n')]
    
    graph_dict = defaultdict(list)
    for (parent, child) in pairs:
        graph_dict[parent].append(child)
    
    vertexes = []
    for item in pairs:
        if item[0] not in vertexes:
            vertexes.append(item[0])
        if item[1] not in vertexes:
            vertexes.append(item[1])
    
    index = {v: i for i, v in enumerate(vertexes)}
    n = len(vertexes)
    
    r1 = np.zeros((n, n), bool)
    for key in graph_dict:
        parent_idx = index[key]
        for child in graph_dict[key]:
            r1[parent_idx][index[child]] = 1
    
    r2 = r1.T
    
    r3 = np.zeros((n, n), bool)
    A = np.dot(r1, r1)
    
    max_path_len = max(len(p) for p in dfs(graph_dict, pairs[0][0]))
    for i in range(max_path_len - 2):
        r3[np.logical_or(r3, A)] = 1
        A = np.dot(A, r1)
    
    r4 = r3.T
    
    r5 = np.zeros((n, n), bool)
    for parent in graph_dict:
        children = graph_dict[parent]
        if len(children) > 1:
            for i in range(len(children)):
                first_idx = index[children[i]]
                for sibling in children[i + 1:]:
                    second_idx = index[sibling]
                    r5[first_idx][second_idx] = 1
    
    r5[np.logical_or(r5, r5.T)] = 1
    
    return (r1.tolist(), r2.tolist(), r3.tolist(), r4.tolist(), r5.tolist())


def entropy(num: float) -> float:
    if num != 0:
        return -num * log2(num)
    return 0.0


def main(s: str) -> tuple[float, float]:
    relation_matrices = task1(s)
    k = 5
    n = len(relation_matrices[0])
    
    out_connections = np.zeros((n, k), int)
    for relation_idx, matrix in enumerate(relation_matrices):
        for node_idx in range(n):
            out_connections[node_idx][relation_idx] = sum(matrix[node_idx])
    
    H_sum = sum(
        entropy(float(row[i] / sum(row)))
        for i in range(k)
        for row in out_connections
    )
    
    C = -1 / e * log2(1 / e)
    H_ref = C * n * k
    h = H_sum / H_ref
    
    print(H_ref)
    return (round(H_sum, 1), round(h, 1))


csv_string = "1,2\n1,3\n3,4\n3,5"
csv_string1 = "1,2\n2,3\n2,4\n4,5\n4,6"
print(main(csv_string1))