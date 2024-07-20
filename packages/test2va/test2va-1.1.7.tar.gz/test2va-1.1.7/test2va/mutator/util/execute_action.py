from appium.webdriver import WebElement

from ..mappings.maps import ActionMap
from ...parser.types.LibTypes import ParsedData, ActionData
from appium.webdriver.webdriver import WebDriver

from ...util.camel_to_snake import camel_to_snake


def execute_action(driver: WebDriver, element: WebElement, data: ParsedData, action: ActionData):
    library = data["library"]

    getattr(ActionMap[library], camel_to_snake(action["action"]))(element, action, driver)
