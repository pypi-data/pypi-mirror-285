from typing import List

from ...parser.structs.XMLElement import XMLElement
from ...parser.types.LibTypes import CriteriaArgument, NestedCriteria
from appium.webdriver.webdriver import WebDriver

from ...util.camel_to_snake import camel_to_snake


class UiAutomator1Criteria:
    @staticmethod
    # TODO: Implement UiSelector <T> className(@NonNull Class<T> type)
    # This covers the other: UiSelector className(@NonNull String className)
    def class_name(arg: List[CriteriaArgument], _driver: WebDriver, _root: XMLElement):
        def f(e: XMLElement) -> bool:
            return e.tag == arg[0]["content"]

        return f

    @staticmethod
    def from_parent(arg: List[CriteriaArgument | NestedCriteria], driver: WebDriver, root: XMLElement):
        funcs = []

        for criteria in arg:
            func_name = camel_to_snake(criteria["name"])
            funcs.append(getattr(UiAutomator1Criteria, func_name)(
                "criteria" in criteria and criteria["criteria"] or criteria["args"], driver, root))

        def inner(e: XMLElement) -> bool:
            for func in funcs:
                if not func(e):
                    return False

            return True

        def f(e: XMLElement) -> bool:
            return e.find_first_parent(lambda elem: inner(elem)) is not None

        return f

    @staticmethod
    def resource_id(arg: List[CriteriaArgument], _driver: WebDriver, _root: XMLElement):
        def f(e: XMLElement) -> bool:
            return e.get("resource-id") == arg[0]["content"]

        return f

    @staticmethod
    def text(arg: List[CriteriaArgument], _driver: WebDriver, _root: XMLElement):
        def f(e: XMLElement) -> bool:
            return e.get("text") == arg[0]["content"]

        return f
