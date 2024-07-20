from typing import List

from test2va.const.const import NSURL
from test2va.parser.structs.XMLElement import XMLElement

from test2va.util.filter_list import filter_list
from test2va.util.map_list import map_list


def find_setup_method(root: XMLElement) -> XMLElement | None:
    # First we are going to find all annotation tags.
    res = root.find_descendants(lambda e: e.tag == f"{{{NSURL}}}annotation")
    # Then we are going to filter these out to only find the ones with a name tag with "Before".
    test_methods = filter_list(res,
                               lambda e: e.find_descendants(
                                   lambda ele: ele.tag == f"{{{NSURL}}}name" and ele.text == "Before"))
    # These match annotation tags however, we need function tags.
    # So, we find the first ancestor which is a function tag.
    if len(test_methods) == 0:
        return None

    return map_list(test_methods, lambda e: e.find_first_ancestor(lambda ele: ele.tag == f"{{{NSURL}}}function"))[0]
