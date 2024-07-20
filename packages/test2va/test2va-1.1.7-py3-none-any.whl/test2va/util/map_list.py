from typing import List, Callable


def map_list(lst: List, callback: Callable) -> List:
    mapped_list = []

    for item in lst:
        mapped_item = callback(item)
        mapped_list.append(mapped_item)

    return mapped_list
