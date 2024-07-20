from appium.webdriver import WebElement


def get_element_info(e: WebElement, xpath: str) -> dict:
    return {
        "xpath": xpath,
        "displayed": e.is_displayed(),
        "content-desc": e.get_attribute("content-desc"),
        "resource-id": e.get_attribute("resource-id"),
        "text": e.get_attribute("text"),
        "checked": e.get_attribute("checked"),
        "enabled": e.get_attribute("enabled"),
        "selected": e.get_attribute("selected"),
    }
