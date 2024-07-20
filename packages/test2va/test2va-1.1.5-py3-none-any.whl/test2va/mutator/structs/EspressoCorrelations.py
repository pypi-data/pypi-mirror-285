from appium.webdriver import WebElement
from test2va.parser.types.LibTypes import CriteriaData


class EspressoCorrelations:
    @staticmethod
    def with_text(element: WebElement, cc: CriteriaData):
        # Happens with something like "containsString"
        if "name" in cc["args"][0]:
            original_content = cc["args"][0]["args"][0]["content"]
            cc["args"][0]["args"][0]["content"] = element.text

            def restore():
                cc["args"][0]["args"][0]["content"] = original_content
        else:
            original_content = cc["args"][0]["content"]
            cc["args"][0]["content"] = element.text

            def restore():
                cc["args"][0]["content"] = original_content

        return restore

    @staticmethod
    def with_id(element: WebElement, cc: CriteriaData):
        original_content = cc["args"][0]["content"]
        cc["args"][0]["content"] = element.get_attribute("resource-id")

        def restore():
            cc["args"][0]["content"] = original_content

        return restore
