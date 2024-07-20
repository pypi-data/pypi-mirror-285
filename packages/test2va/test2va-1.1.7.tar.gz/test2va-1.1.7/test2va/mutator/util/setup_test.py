from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from ...const.const import FIND_ELEMENT_WAIT
from ..util.build_xpath_from_element import build_xpath_from_element
from ..util.execute_action import execute_action
from ..util.find_xml_element import find_xml_element
from ...parser.types.LibTypes import ParsedData
from selenium.webdriver.support import expected_conditions as ec


def setup_test(driver: WebDriver, data: ParsedData, second=False):
    test_func_selectors = data["before"]

    for selector in test_func_selectors:
        # Attempt to find corresponding XML element given by the selector criteria.
        matched_element, xpath, _ = find_xml_element(driver, selector)

        # This deals with loading. If it worked the first time, it must work again.
        while second and matched_element is None:
            matched_element, xpath, _ = find_xml_element(driver, selector)

        if matched_element is None:
            print("Element not found during test setup execution.")
            print("Test Setup Failed.")
            exit(1)

        # We are going to find the element via xpath and execute the action on it to run through the test setup.
        try:
            wait = WebDriverWait(driver, FIND_ELEMENT_WAIT)
            element = wait.until(ec.presence_of_element_located((AppiumBy.XPATH, xpath)))
        except (TimeoutException, NoSuchElementException):
            print(f"Element not found during test setup execution: {xpath}")
            print("Test Setup Failed.")
            exit(1)

        execute_action(driver, element, data, selector["action"])
