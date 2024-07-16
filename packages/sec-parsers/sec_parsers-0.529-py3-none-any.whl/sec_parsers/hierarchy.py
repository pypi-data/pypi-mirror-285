from collections import defaultdict

# TODO: Add more comments to the functions, refactor

# Module to take parsed headers and determine the hierarchy of the headers

# Highly WIP
def get_hierarchy_from_list(parsing_list):
    seen = set()
    result = []
    for parsing_string in parsing_list:
        if parsing_string not in seen:
            seen.add(parsing_string)
            result.append(parsing_string)
    return result

def split_list(parsing_list):
    lsts = []
    lst = []
    for parsing_string in parsing_list:
        if ((parsing_string == 'item;') or (parsing_string == 'part;')):
            if len(lst) > 0:
                lsts.append(lst)
            lst = []
        else:
            lst.append(parsing_string)

    return lsts

def get_hierarchy_from_lists(lsts):
    # Initialize the counter dictionary
    pair_counts = defaultdict(int)

    # Update counts for each pair
    for lst in lsts:
        for i in range(len(lst) - 1):
            pair = (lst[i], lst[i + 1])
            pair_counts[pair] += 1

    # Convert pair counts to a list of tuples and sort by count
    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)

    # Initialize a set to keep track of visited elements
    visited = set()
    hierarchy = []

    # Build the hierarchy based on sorted pairs
    for (a, b), count in sorted_pairs:
        if a not in visited:
            hierarchy.append(a)
            visited.add(a)
        if b not in visited:
            hierarchy.append(b)
            visited.add(b)

    return hierarchy

# WIP
def get_hierarchy(elements):
    """Calculates the hierarchy."""
    # get lists item --> item, item --> part
    lsts = split_list(elements)
    # get hiereachy lists
    hierarchy_lists = [get_hierarchy_from_list(lst) for lst in lsts]
    # use lists to get hierarchy
    hierarchy = get_hierarchy_from_lists(hierarchy_lists)
    # insert item at beginning
    hierarchy.insert(0,'item;')
    # insert part before item
    hierarchy.insert(0,'part;')
    return hierarchy


def get_preceding_elements(element_list, element):
    """Get the elements that precede the given element in the list."""
    if element in element_list:
        element_index = element_list.index(element)
        return element_list[:element_index]
    else:
        return []

def find_last_index(lst1, lst2):
  """Find the last index of lst1 in lst2."""
  last_index = -1
  for i in range(len(lst1)):
    if lst1[i] in lst2:
      last_index = i
  return last_index

