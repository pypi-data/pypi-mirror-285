from typing import List

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from ...const.const import FIND_ELEMENT_WAIT
from ..util.build_xpath_from_element import build_xpath_from_element
from ..util.find_element import find_element
from ...parser.types.LibTypes import AssertionData
from appium.webdriver.webdriver import WebDriver


# TODO: Implement other assertions other than exists.
def execute_assertion(driver: WebDriver, assertion_data: List[AssertionData]):

    for assertion in assertion_data:
        try:
            assertion_element, xpath = find_element(driver, assertion["selector"])
        except NoSuchElementException:
            return False

        if assertion_element is None:
            return False

        wait = WebDriverWait(driver, FIND_ELEMENT_WAIT)

        # TODO: Formal assertion mapping
        try:
            element = wait.until(ec.presence_of_element_located((AppiumBy.XPATH, xpath)))
            assertion_action = assertion["selector"]["action"]
            if assertion_action["action"] == "matches":
                if assertion_action["args"][0]["name"] == "not":
                    assert not element.is_displayed()
                if assertion_action["args"][0]["name"] == "isDisplayed":
                    assert element.is_displayed()
                # TODO: Assuming withText for now.
                # text = assertion_action["args"][0]["args"][0]["content"]
                # assert element.text == text
            else:
                assert element.is_displayed()
        except TimeoutException:
            return False

    return True

