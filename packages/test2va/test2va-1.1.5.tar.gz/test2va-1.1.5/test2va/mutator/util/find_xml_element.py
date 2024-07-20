import os
import time
import xml.etree.ElementTree as ET

from appium.webdriver.webdriver import WebDriver

from ..mappings.maps import WebElementMap
from ..util.build_xpath_from_element import build_xpath_from_element
from ...parser.structs import XMLElement
from ...parser.types.LibTypes import SelectorData
from ...parser.util.traverse_elements import traverse_elements
from ...util.camel_to_snake import camel_to_snake

# seconds
timeout = 5


# TODO: Implement espresso search-type.
def find_xml_element(driver: WebDriver, selector: SelectorData):
    start = time.time()
    cur = time.time()
    match = None
    while cur - start < timeout:
        # print(match)
        # Get the current page source as XML.
        current_page_src = driver.page_source  # get_static_page_source(driver)

        # Library to find the right criteria mapping.
        library = selector["type"]

        target_map = WebElementMap[library]

        # Write the XML file, so it can be traversed and analyzed.
        with open("temp.xml", "w", encoding="utf-8") as f:
            f.write(current_page_src)

        tree = ET.parse("temp.xml")
        root = traverse_elements(tree.getroot())

        # Matching functions.
        # TODO: Only supports allOf
        functions = []
        for criteria in selector["criteria"]:
            func_name = camel_to_snake(criteria["name"])
            functions.append(getattr(target_map, func_name)(
                "criteria" in criteria and criteria["criteria"] or criteria["args"], driver, root))

        # Execute the matching functions.
        def exe(e: XMLElement) -> bool:
            for func in functions:
                if not func(e):
                    return False

            return True

        element = root.find_first_descendant(lambda e: exe(e))

        if element is not None:
            # This can be flaky because it may find a match in motion from transitions. Meaning, the bounds will be off.
            # The bounds cannot be left out because they are important to discriminate between similar elements.
            # So, we will have to keep checking until the element is static.
            xpath = build_xpath_from_element(element)
            if match is None:
                cur = time.time()
                match = xpath
            elif match == xpath:
                os.remove("temp.xml")
                return element, xpath, len(root.find_descendants(lambda e: True))
            else:
                cur = time.time()
                match = xpath
        else:
            cur = time.time()

        time.sleep(0.1)

    os.remove("temp.xml")

    return None, None, None
