import json
import re
from typing import TextIO

from test2va.generator.core.GUI import GUIEvent, GUIMethod, GUIElement, GUIControl
from test2va.generator.core.GUI import (TEXT_FEATURE_CONSTANT_STRING, CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING,
                                            RESOURCE_ID_FEATURE_CONSTANT_STRING, CLASS_FEATURE_CONSTANT_STRING, 
                                            DISPLAYED_FEATURE_CONSTANT_STRING)


def get_class_name_from_xpath(xpath: str):
    pattern = r"\/\/(.*?)\["
    match = re.search(pattern, xpath)

    if match:
        class_name = match.group(1)
        return class_name
    else:
        return None


def import_events_from_basic_test_script(file_path: str) -> GUIMethod:
    """
    This method read the file_path of parsed basic test script and convert it to an GUIMethod object
    :param file_path: file path
    :return: GUIMethod obj
    """
    # Open the JSON file
    with open(file_path, 'r') as file:
        # Load the data from the file
        json_data = json.load(file)
        return GUIMethod(json_data)


def update_element(report_result: dict, old_element: GUIElement = None):
    """
    Parse the result from detector like this below:
    {
      "xpath": "//android.widget.CheckedTextView[...]",
      "displayed": true,
      "content-desc": null,
      "resource-id": "com.maltaisn.notes.sync:id/design_menu_item_text",
      "text": "Create new label",
      "checked": "false",
      "enabled": "true",
      "selected": "false"
    }
    to an GUI element obj.
    Support features list: 'text', 'content-desc', 'resource-id', 'class', 'displayed'

    If old_element=None, create a new element, else update the existing element
    also update the prior id

    :param report_result:
    :param old_element:
    :return:
    """

    if old_element is None:
        new_element: GUIElement = GUIElement()
    else:
        new_element: GUIElement = old_element

    new_element.set_feature(TEXT_FEATURE_CONSTANT_STRING, report_result[TEXT_FEATURE_CONSTANT_STRING])
    new_element.set_feature(CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING,
                            report_result[CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING])
    new_element.set_feature(RESOURCE_ID_FEATURE_CONSTANT_STRING, report_result[RESOURCE_ID_FEATURE_CONSTANT_STRING])
    new_element.set_feature(CLASS_FEATURE_CONSTANT_STRING, get_class_name_from_xpath(report_result['xpath']))
    new_element.set_feature(DISPLAYED_FEATURE_CONSTANT_STRING, report_result[DISPLAYED_FEATURE_CONSTANT_STRING])

    # update the prior_id
    new_element.update_prior_id()

    return new_element


def update_events_from_basic_path_in_detection_result(basic_method: GUIMethod, detection_result_path: str):
    """
    update the feature details of element in events by scanning the basic path in mutant detection result.
    This update help gather the missing info from the static parsed result in test method
    :param basic_method:
    :param detection_result_path:
    :return:
    """
    with open(detection_result_path, 'r') as file:
        # 1. Load the data from the file
        json_data = json.load(file)

        # 2. loop
        length = len(basic_method.get_events())
        index = 0
        mutant_count = 0
        while index < length:
            # get event and its element
            new_event = basic_method.get_event_by_index(index)
            old_element = new_event.get_gui_element()

            # update the new element
            new_element = update_element(json_data['basic_path'][index], old_element)

            # update the new event
            new_event.set_gui_element(new_element)

            # update the event in method
            basic_method.set_event_by_index(new_event, index)

            # go to next event
            index = index + 1

    return basic_method


def get_gui_method(task_parsed_report_path, task_mutant_report_path) -> GUIMethod:
    basic_method = import_events_from_basic_test_script(task_parsed_report_path)
    updated_method = update_events_from_basic_path_in_detection_result(basic_method, task_mutant_report_path)

    return updated_method
