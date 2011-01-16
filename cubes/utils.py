"""Utility functions for computing combinations of dimensions and hierarchy levels"""

import itertools

def node_level_points(node):
    """Get all level points within given node. Node is described as tuple: (object, levels)
    where levels is a list or a tuple"""
    
    levels = []
    points = []
    for level in node[1]:
        levels.append(level)
        points.append( (node, tuple(levels)))
        
    return points

def combine_node_levels(nodes):
    """Get all possible combinations between each level from each node. It is a cartesian
    product of first node levels and all combinations of the rest of the levels"""

    if not nodes:
        raise Exception("List of nodes is empty")
    if len(nodes) == 1:
        current_node = nodes[0]
        points = node_level_points(current_node)

        # Combos is a list of one-item lists:
        # combo = (item) => ( ( (name, (level,...)), (plevel, ...)) )
        # item = (node, plevels) => ( (name, (level,...)), (plevel, ...))
        # node = (name, levels) => (name, (level,...))
        # levels = (level)
        
        combos = []
        for point in points:
            combos.append( (point, ) )

        return combos
    else:
        current_node = nodes[0]
        current_name = current_node[0]
        other_nodes = nodes[1:]

        current_points = node_level_points(current_node) # LIST OF POINTS
        other_points = combine_node_levels(other_nodes) # LIST OF POINTS ???

        
        combos = []

        for combo in itertools.product(current_points, other_points):
            res = (combo[0], ) + combo[1]
            combos.append(res)
        
        return list(combos)

def combine_nodes(all_nodes, required_nodes = []):
    """Create all combinations of nodes, if required_nodes are specified, make them present in each
    combination."""
    
    other_nodes = []

    if not all_nodes:
        return []

    if not required_nodes:
        required_nodes = []

    for node in all_nodes:
        if node not in required_nodes:
            other_nodes.append(node)
    
    all_combinations = []

    if required_nodes:
        all_combinations += combine_node_levels(required_nodes)
    
    if other_nodes:
        for i in range(1, len(other_nodes) + 1):
            combo_nodes = itertools.combinations(other_nodes, i)
            for combo in combo_nodes:
                out = combine_node_levels(required_nodes + list(combo))
                all_combinations += out

    return all_combinations
    
def compute_dimension_cell_selectors(dimensions, required = []):
    """Create selector for all possible combinations of dimensions for each levels in hierarchical
    order.
    
    Returns list of dimension selectors. Each dimension selector is a list of tuples where first element
    is a dimension and second element is list of levels. Order of selectors and also dimensions within
    selector is undefined.

    *Example 1*:

    If there are no hierarchies (dimensions are flat), then this method returns all combinations of all
    dimensions. If there are dimensions A, B, C with single level a, b, c, respectivelly, the output
    will be:
    
    Output::
    
        (A, (a)) 
        (B, (b)) 
        (C, (c)) 
        (A, (a)), (B, (b))
        (A, (a)), (C, (c))
        (B, (b)), (C, (c))
        (A, (a)), (B, (b)), (C, (c))

    *Example 2*:
    
    Take dimensions from example 1 and add requirement for dimension A (might be date usually). then
    the youtput will contain dimension A in each returned tuple. Tuples without dimension A will
    be ommited.

    Output::
    
        (A, (a)) 
        (A, (a)), (B, (b))
        (A, (a)), (C, (c))
        (A, (a)), (B, (b)), (C, (c))

    *Example 3*:
    
    If there are multiple hierarchies, then all levels are combined. Say we have D with d1, d2, B with 
    b1, b2, and C with c. D (as date) is required:
    
    Output::
    
        (D, (d1))
        (D, (d1, d2))
        (D, (d1)),     (B, (b1))
        (D, (d1, d2)), (B, (b1))
        (D, (d1)),     (B, (b1, b2))
        (D, (d1, d2)), (B, (b1, b2))
        (D, (d1)),     (B, (b1)),     (C, (c))
        (D, (d1, d2)), (B, (b1)),     (C, (c))
        (D, (d1)),     (B, (b1, b2)), (C, (c))
        (D, (d1, d2)), (B, (b1, b2)), (C, (c))
        
    """
    
    all_nodes = []
    required_nodes = []
    
    for dim in required:
        if dim not in dimensions:
            raise AttributeError("Required dimension '%s' does not exist in list of computed "\
                                 "dimensions" % dim.name)
        required_nodes.append( (dim, dim.levels) )

    for dim in dimensions:
        all_nodes.append( (dim, dim.levels) )        
        
    combos = combine_nodes(all_nodes, required_nodes)

    result = []
    for combo in combos:
        new_selector = []
        for selector in combo:
            dim = selector[0][0]
            levels = selector[1]
            new_selector.append( (dim, levels) )
        result.append(new_selector)
            
    return result

def expand_dictionary(record, separator = '.'):
    """Return expanded dictionary: treat keys are paths separated by `separator`, create
    sub-dictionaries as necessary"""
    result = {}
    for key, value in record.items():
        current = result
        path = key.split(separator)
        for part in path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[path[-1]] = value
    return result