import json
import ast
from typing import List, Dict, Tuple


def calculate_membership(value: float, points: List[List[float]]) -> float:
    x1, y1 = points[0]
    x2, y2 = points[1]
    x3, y3 = points[2]
    x4, y4 = points[3]
    
    if value < x1:
        return y1
    elif x1 <= value < x2:
        if x2 == x1:
            return y1
        return y1 + (y2 - y1) * (value - x1) / (x2 - x1)
    elif x2 <= value <= x3:
        return y2
    elif x3 < value <= x4:
        if x4 == x3:
            return y3
        return y3 + (y4 - y3) * (value - x3) / (x4 - x3)
    else:
        return y4


def fuzzify_input(temperature: float, temp_sets: List[Dict]) -> Dict[str, float]:
    memberships = {}
    for term in temp_sets:
        membership = calculate_membership(temperature, term["points"])
        memberships[term["id"]] = membership
    return memberships


def find_matching_term(term_name: str, available_terms: Dict[str, List]) -> str:
    if term_name in available_terms:
        return term_name
    
    mappings = {
        "нормально": "комфортно",
        "интенсивно": "интенсивный",
        "умеренно": "умеренный",
        "слабо": "слабый"
    }
    
    if term_name in mappings and mappings[term_name] in available_terms:
        return mappings[term_name]
    
    term_lower = term_name.lower()
    best_match = None
    best_match_length = 0
    
    for key in available_terms.keys():
        key_lower = key.lower()
        if term_lower in key_lower or key_lower in term_lower:
            match_length = min(len(term_lower), len(key_lower))
            if match_length > best_match_length:
                best_match = key
                best_match_length = match_length
    
    if best_match is None:
        for key in available_terms.keys():
            key_lower = key.lower()
            for prefix_len in range(6, 3, -1):
                if (len(term_lower) >= prefix_len and len(key_lower) >= prefix_len and
                    term_lower[:prefix_len] == key_lower[:prefix_len]):
                    return key
    
    return best_match


def apply_rule(activation: float, output_points: List[List[float]], 
               x_values: List[float]) -> List[float]:
    result = []
    for x in x_values:
        mu_output = calculate_membership(x, output_points)
        result.append(min(activation, mu_output))
    return result


def aggregate_rules(rule_outputs: List[List[float]]) -> List[float]:
    if not rule_outputs:
        return []
    
    n = len(rule_outputs[0])
    aggregated = []
    
    for i in range(n):
        max_val = max(output[i] for output in rule_outputs)
        aggregated.append(max_val)
    
    return aggregated


def defuzzify_first_max(memberships: List[float], x_values: List[float]) -> float:
    if not memberships:
        return 0.0
    
    max_membership = max(memberships)
    
    for i, membership in enumerate(memberships):
        if membership == max_membership:
            return x_values[i]
    
    return x_values[0]


def main(temp_sets_json: str, 
         control_sets_json: str, 
         rules_json: str, 
         temperature: float) -> float:
    
    temp_data = json.loads(temp_sets_json)
    control_data = json.loads(control_sets_json)
    
    try:
        rules = json.loads(rules_json)
    except json.JSONDecodeError:
        rules = ast.literal_eval(rules_json)
    
    temp_sets = next(v for v in temp_data.values() if isinstance(v, list))
    control_sets = next(v for v in control_data.values() if isinstance(v, list))
    
    min_x = float('inf')
    max_x = float('-inf')
    for term in control_sets:
        for point in term["points"]:
            min_x = min(min_x, point[0])
            max_x = max(max_x, point[0])
    
    step = 0.1
    x_values = []
    x = min_x
    while x <= max_x:
        x_values.append(x)
        x += step
    
    temp_memberships = fuzzify_input(temperature, temp_sets)
    
    temp_dict = {term["id"]: term["points"] for term in temp_sets}
    control_dict = {term["id"]: term["points"] for term in control_sets}
    
    rule_outputs = []
    
    for input_term_name, output_term_name in rules:
        input_term = find_matching_term(input_term_name, temp_dict)
        output_term = find_matching_term(output_term_name, control_dict)
        
        if input_term is None or output_term is None:
            continue
        
        activation = temp_memberships.get(input_term, 0.0)
        output_points = control_dict[output_term]
        
        rule_output = apply_rule(activation, output_points, x_values)
        rule_outputs.append(rule_output)
    
    aggregated = aggregate_rules(rule_outputs)
    result = defuzzify_first_max(aggregated, x_values)
    
    return result


__all__ = ["main"]