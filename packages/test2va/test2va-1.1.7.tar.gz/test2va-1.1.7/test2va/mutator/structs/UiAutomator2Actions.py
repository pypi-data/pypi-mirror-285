from appium.webdriver import WebElement
from appium.webdriver.webdriver import WebDriver

from ...parser.types.LibTypes import ActionData


class UiAutomator2Actions:
    @staticmethod
    def click(element: WebElement, _action: ActionData, _driver: WebDriver):
        element.click()

    @staticmethod
    def set_text(element: WebElement, action: ActionData, _driver: WebDriver):
        element.send_keys(action["args"][0]["content"])
