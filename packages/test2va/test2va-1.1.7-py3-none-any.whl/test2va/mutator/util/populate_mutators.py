from appium.webdriver.webdriver import WebDriver

from ..util.build_xpath_from_element import build_xpath_from_element
from ...parser.structs import XMLElement
from ...util.filter_list import filter_list


def populate_mutators(_driver: WebDriver, mutators: list, element: XMLElement, text: str = None):
    indices = set()

    if text is not None:
        mut_str = "text="
        for c in text:
            if c.isalpha():
                mut_str += "a"
            elif c.isdigit():
                mut_str += "1"
            else:
                mut_str += c
        mutators.append(mut_str)
        return

    indices.add(element.index())

    # First, element siblings with same class
    siblings = filter_list(element.get_siblings(), lambda e: e.get("class") == element.get("class"))
    for sibling in siblings:
        mutators.append(build_xpath_from_element(sibling))
        indices.add(sibling.index())

    parent = element
    while parent.get_parent() is not None:
        # print("Parent: " + parent.get("class"))
        parent = parent.get_parent()

        p_desc = parent.find_descendants(
            lambda e: e.get("class") == element.get(
                "class") and e.index() not in indices and e.depth() == element.depth() and e.get(
                "index") == element.get("index")
        )

        for desc in p_desc:
            mutators.append(build_xpath_from_element(desc))
            indices.add(desc.index())
