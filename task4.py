import json
import numpy as np
from typing import Any, List, Dict

def normalize_to_list(item: Any) -> List:
    return item if isinstance(item, list) else [item]

def flatten_ranking(ranking: List) -> List:
    flattened = []
    for group in ranking:
        flattened.extend(normalize_to_list(group))
    return flattened

def build_preference_matrix(ranking: List, items: List) -> np.ndarray:
    n = len(items)
    item_to_index = {item: idx for idx, item in enumerate(items)}
    matrix = np.zeros((n, n), dtype=int)
    
    for level, current_group in enumerate(ranking):
        current_group = normalize_to_list(current_group)
        
        for item in current_group:
            item_idx = item_to_index[item]
            matrix[item_idx, :] = 1
        
        for previous_group in ranking[:level]:
            previous_group = normalize_to_list(previous_group)
            for current_item in current_group:
                current_idx = item_to_index[current_item]
                for previous_item in previous_group:
                    previous_idx = item_to_index[previous_item]
                    matrix[current_idx, previous_idx] = 0
                    matrix[previous_idx, current_idx] = 1
    
    return matrix

def find_contradictions(matrix_a: np.ndarray, matrix_b: np.ndarray, items: List) -> List[List]:
    n = len(items)
    contradictions = []
    
    for i in range(n):
        for j in range(i + 1, n):
            a_prefers_i_over_j = matrix_a[i, j] == 1 and matrix_a[j, i] == 0
            b_prefers_j_over_i = matrix_b[i, j] == 0 and matrix_b[j, i] == 1
            
            if a_prefers_i_over_j and b_prefers_j_over_i:
                contradictions.append([items[i], items[j]])
            
            a_prefers_j_over_i = matrix_a[i, j] == 0 and matrix_a[j, i] == 1
            b_prefers_i_over_j = matrix_b[i, j] == 1 and matrix_b[j, i] == 0
            
            if a_prefers_j_over_i and b_prefers_i_over_j:
                contradictions.append([items[j], items[i]])
    
    return contradictions

def build_consensus_ranking(items: List, contradictions: List[List]) -> List:
    conflict_map: Dict[Any, List] = {}
    for item_a, item_b in contradictions:
        conflict_map.setdefault(item_a, []).append(item_b)
    
    result = []
    processed = set()
    
    for item in items:
        if item in processed:
            continue
        
        if item in conflict_map:
            group = [item]
            processed.add(item)
            
            for conflicting_item in conflict_map[item]:
                if conflicting_item not in processed:
                    group.append(conflicting_item)
                    processed.add(conflicting_item)
            
            result.append(group)
        else:
            result.append(item)
            processed.add(item)
    
    return result

def merge_rankings(json_ranking_a: str, json_ranking_b: str) -> str:
    ranking_a = json.loads(json_ranking_a)
    ranking_b = json.loads(json_ranking_b)
    
    all_items = sorted(set(flatten_ranking(ranking_a)) | set(flatten_ranking(ranking_b)))
    
    matrix_a = build_preference_matrix(ranking_a, all_items)
    matrix_b = build_preference_matrix(ranking_b, all_items)
    
    contradictions = find_contradictions(matrix_a, matrix_b, all_items)
    consensus_ranking = build_consensus_ranking(all_items, contradictions)
    
    return json.dumps(consensus_ranking, ensure_ascii=False)

if __name__ == "__main__":
    ranking_a = json.dumps([1, [2, 3], 4, [5, 6, 7], 8, 9, 10])
    ranking_b = json.dumps([[1, 2], [3, 4, 5], 6, 7, 9, [8, 10]])
    print(merge_rankings(ranking_a, ranking_b))