from typing import Callable

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from test2va.const.const import FIND_ELEMENT_WAIT
from test2va.mutator.mappings.maps import AssertionCorrelationMap
from test2va.mutator.util.base_test import base_test
from test2va.mutator.util.clear_user_data import clear_user_data
from test2va.mutator.util.execute_action import execute_action
from test2va.mutator.util.execute_assertion import execute_assertion
from test2va.mutator.util.find_assertion_correlations import find_correlations
from test2va.mutator.util.find_element import find_element
from test2va.mutator.util.get_element_info import get_element_info
from test2va.mutator.util.grant_permissions import grant_permissions
from test2va.mutator.util.setup_test import setup_test
from test2va.parser.types.LibTypes import ParsedData
from test2va.util.camel_to_snake import camel_to_snake


def mutator(driver: WebDriver, data: ParsedData, auto_grant_perms):
    # Where the potential mutators are stored.
    mutators = []

    app_id = driver.current_package

    paths = {}

    # First, we will set up the test if it had a setup function
    if data["before"] is not None:
        setup_test(driver, data)

    # Then, we will execute the base test to make sure that it works properly as given.
    # At the same time, at each step, we will populate relevant potential mutators.
    element_count = []
    basic_path = []
    base_test(mutators, driver, data, element_count, basic_path)

    paths["basic_path"] = basic_path

    correlations = find_correlations(data)

    selectors = data["selectors"]
    assertion = data["assertion"]

    wait = WebDriverWait(driver, FIND_ELEMENT_WAIT)

    paths["assertion_correlations"] = {}

    paths["candidates_before"] = element_count

    for i in range(len(correlations)):
        if correlations[i]:
            key = f"assertion_{i}"
            paths["assertion_correlations"][key] = {}
            paths["assertion_correlations"][key]["event_correlation"] = correlations[i]["event"]
            paths["assertion_correlations"][key]["potential_replacements"] = mutators[correlations[i]["event"]]

    target = 0
    while target < len(mutators):
        # Setting the target mutators to the pool of the respective step in the test.
        target_mutators = mutators[target]

        paths[target] = {"mutable": False, "attempted_paths": [], "successful_paths": []}

        while len(target_mutators) > 0:
            # Reset the app to start at the same place.
            driver.terminate_app(app_id)
            clear_user_data(driver, app_id)
            if auto_grant_perms:
                grant_permissions(driver, app_id)
            driver.activate_app(app_id)

            if data["before"] is not None:
                setup_test(driver, data, True)

            cur_path = []
            paths[target]["attempted_paths"].append(cur_path)

            restore: Callable = None

            for i in range(len(mutators)):
                # If the current step is the target step, then we need to mutate the target element.
                if i == target:
                    try:
                        if target_mutators[0].startswith("text="):
                            text_mut = target_mutators[0].split("text=")[1]
                            element, xpath = find_element(driver, selectors[i])

                            element_data = get_element_info(element, xpath)

                            execute_action(driver, element, data, {"action": selectors[i]["action"]["action"],
                                                                   "args": [{"type": "string", "content": text_mut}]})

                            for correlation in correlations:
                                if correlation is not None and correlation["event"] == i:
                                    restore = getattr(AssertionCorrelationMap[data["library"]],
                                                      camel_to_snake(correlation["corresponding_criteria"]["name"]))(
                                        element, correlation["corresponding_criteria"])
                                    break
                        else:
                            xpath = target_mutators[0]
                            element = wait.until(ec.presence_of_element_located((AppiumBy.XPATH, xpath)))

                            element_data = get_element_info(element, xpath)

                            for correlation in correlations:
                                if correlation is not None and correlation["event"] == i:
                                    restore = getattr(AssertionCorrelationMap[data["library"]],
                                                      camel_to_snake(correlation["corresponding_criteria"]["name"]))(
                                        element, correlation["corresponding_criteria"])
                                    break

                            execute_action(driver, element, data, selectors[target]["action"])
                    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                        if restore is not None:
                            restore()
                        print("Element not found by XPATH. Continuing execution...")
                        break
                # Otherwise, we need to execute an action on the element as normal.
                else:
                    try:
                        element, xpath = find_element(driver, selectors[i])

                        element_data = get_element_info(element, xpath)

                        execute_action(driver, element, data, selectors[i]["action"])
                    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                        print("Element not found. Continuing execution...")
                        break

                cur_path.append(element_data)

            if execute_assertion(driver, assertion):
                paths[target]["mutable"] = True
                paths[target]["attempted_paths"].pop()
                paths[target]["successful_paths"].append(cur_path)
                target_mutators.pop(0)
                print("Assertion passed.")

                if restore is not None:
                    restore()
            else:
                # Failed assertion. Remove the current mutator and try the next one.
                print("Assertion failed. Trying next mutator...")
                target_mutators.pop(0)
                if restore is not None:
                    restore()

        target += 1

    return paths
