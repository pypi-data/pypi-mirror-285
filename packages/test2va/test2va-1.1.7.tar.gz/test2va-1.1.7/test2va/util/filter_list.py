from typing import List, Callable


def filter_list(lst: List, callback: Callable) -> List:
    filtered_list = []

    for item in lst:
        if callback(item):
            filtered_list.append(item)

    return filtered_list
