from appium.webdriver import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from ...const.const import FIND_ELEMENT_WAIT
from ..util.build_xpath_from_element import build_xpath_from_element
from ..util.find_xml_element import find_xml_element
from ...parser.types.LibTypes import SelectorData


def find_element(driver: WebDriver, selector: SelectorData) -> (WebElement, str):
    matched_element, xpath, _ = find_xml_element(driver, selector)

    if matched_element is None:
        raise NoSuchElementException("Could not find element in base test.")

    wait = WebDriverWait(driver, FIND_ELEMENT_WAIT)
    return wait.until(ec.presence_of_element_located((AppiumBy.XPATH, xpath))), xpath
