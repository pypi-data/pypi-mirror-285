import os
import xml.etree.ElementTree as ET
from typing import Literal

from test2va.const.const import NSURL
from test2va.exceptions import SRCMLError, JSONError
from test2va.parser.structs.UiAutomator1ExprElement import UiAutomator1ExprElement
from test2va.parser.structs.UiAutomator2ExprElement import UiAutomator2ExprElement
from test2va.parser.structs.EspressoDeclElement import EspressoDeclElement
from test2va.parser.types.LibTypes import ParsedData
from test2va.parser.util.find_all_test_methods import find_all_test_methods
from test2va.parser.util.find_setup_method import find_setup_method
#from test2va.parser.util.modify_srcml import modify_srcml
from test2va.parser.util.traverse_elements import traverse_elements
from test2va.util.write_json import write_json


def parser(output_path, java_path, events):
    # srcml must be installed on the local machine.
    # The module has a hard time finding the dll path.
    '''
    try:
        modify_srcml(gui.srcml_input_text.get())
    except Exception as e:
        gui.out(f"⛔ SRCML Path Error: {e}")
        gui.out("⚠️ Verify srcml dll file path")
        return
    '''

    #from pylibsrcml import srcml

    xml = "temp.xml"

    try:
        # Run a command from the
        os.system(f"srcml {java_path} -o {xml}")
        #srcml.srcml(gui.java_input_text.get(), xml)
    except Exception as e:
        raise SRCMLError(f"Verify input java file & srcml installation. Is it added to PATH?", events)

    tree = ET.parse(xml)
    root = traverse_elements(tree.getroot())

    # The first thing to do is to find all the test methods.
    test_methods = find_all_test_methods(root)

    # Next find a setup method
    setup_method = find_setup_method(root)

    # This is the cache that will store the data.
    data = []

    # Now we need to get the data for each method.
    for method in test_methods:
        name = method.find_first_child(lambda e: e.tag == f"{{{NSURL}}}name").text

        if len(UiAutomator1ExprElement.find_selector_structures(method)) > 0:
            lib: Literal["UiAutomator1"] = "UiAutomator1"
            clazz = UiAutomator1ExprElement
        elif len(UiAutomator2ExprElement.find_selector_structures(method)) > 0:
            lib: Literal["UiAutomator2"] = "UiAutomator2"
            clazz = UiAutomator2ExprElement
        else:
            lib: Literal["Espresso"] = "Espresso"
            clazz = EspressoDeclElement

        method_data: ParsedData = {
            "name": name,
            "selectors": [],
            "before": [],
            "assertion": [],
            "library": lib
        }

        # Get all selectors for this method.
        selectors = clazz.find_selector_structures(method)

        # Get setup selectors
        if setup_method is not None:
            setup_selectors = clazz.find_selector_structures(setup_method)
            for selector in setup_selectors:
                method_data["before"].append(selector.get_data())
        else:
            method_data["before"] = None

        # Cache all the selector data
        for selector in selectors:
            method_data["selectors"].append(selector.get_data())

        method_data["assertion"] = clazz.parse_assertion(method)

        data.append(method_data)

    try:
        write_json(data, output_path)
    except Exception as e:
        raise JSONError(f"Parse data JSON write error.", events)

    os.remove(xml)

    return data
