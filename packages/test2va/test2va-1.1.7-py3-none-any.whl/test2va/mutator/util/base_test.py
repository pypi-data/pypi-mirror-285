from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from ...const.const import FIND_ELEMENT_WAIT
from ..mappings.maps import TextActionMap
from ..util.build_xpath_from_element import build_xpath_from_element
from ..util.execute_action import execute_action
from ..util.find_xml_element import find_xml_element
from ..util.get_element_info import get_element_info
from ..util.populate_mutators import populate_mutators
from ...parser.types.LibTypes import ParsedData
from selenium.webdriver.support import expected_conditions as ec


def base_test(mutators, driver: WebDriver, data: ParsedData, element_count: list, base_path: list):
    test_func_selectors = data["selectors"]

    for selector in test_func_selectors:
        # Attempt to find corresponding XML element given by the selector criteria.
        matched_element, xpath, tot_elements = find_xml_element(driver, selector)

        if matched_element is None:
            print("Element not found during base test execution.")
            print("Base Test Failed.")
            exit(1)

        # We are going to find the element via xpath and execute the action on it to run through the base test.
        # At the same time we are going to populate the mutators.
        try:
            wait = WebDriverWait(driver, FIND_ELEMENT_WAIT)
            element = wait.until(ec.presence_of_element_located((AppiumBy.XPATH, xpath)))
        except (TimeoutException, NoSuchElementException):
            print(f"Element not found during base test execution: {xpath}")
            print("Base Test Failed.")
            exit(1)

        element_info = get_element_info(element, xpath)

        base_path.append(element_info)

        element_mutators = []

        mutators.append(element_mutators)

        populate_mutators(driver, element_mutators, matched_element, selector["action"]["args"][0]["content"] if selector["action"]["action"] in TextActionMap else None)

        execute_action(driver, element, data, selector["action"])

        element_count.append(tot_elements)