from appium.webdriver import WebElement
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver import ActionChains

from ...parser.types.LibTypes import ActionData


class EspressoActions:
    @staticmethod
    def click(element: WebElement, _action: ActionData, _driver: WebDriver):
        element.click()

    @staticmethod
    def close_soft_keyboard(_element: WebElement, action: ActionData, driver: WebDriver):
        driver.hide_keyboard()

    @staticmethod
    def long_click(element: WebElement, _action: ActionData, driver: WebDriver):
        actions = ActionChains(driver)
        actions.move_to_element(element).click_and_hold().perform()

    @staticmethod
    def press_ime_action_button(element: WebElement, action: ActionData, driver: WebDriver):
        driver.press_keycode(66)

    @staticmethod
    def press_back(element: WebElement, action: ActionData, driver: WebDriver):
        driver.press_keycode(4)

    @staticmethod
    def replace_text(element: WebElement, action: ActionData, driver: WebDriver):
        element.clear()
        element.send_keys(action["args"][0]["content"])

    @staticmethod
    def type_text(element: WebElement, action: ActionData, driver: WebDriver):
        element.send_keys(action["args"][0]["content"])
