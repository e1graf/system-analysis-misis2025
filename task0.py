from typing import List
from collections import defaultdict

def main(csv: str) -> List[List]:
    csv_edges = [edge.split(",") for edge in csv.split("\n")]
    
    vertex_neighbors = defaultdict(list)
    vertices = set()
    
    for edge in csv_edges:
        vertices.add(edge[0])
        vertices.add(edge[1])
        vertex_neighbors[edge[0]].append(edge[1])
    
    print(vertices)
    
    graph = []
    for vertex_out in vertices:
        neighbors = set(vertex_neighbors[vertex_out])
        row = [1 if vertex_in in neighbors else 0 for vertex_in in vertices]
        graph.append(row)
    
    return graph

for row in main("1,2\n1,3\n3,4\n3,5"):
    print(row)