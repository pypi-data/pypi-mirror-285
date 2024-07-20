from typing import List

from ...parser.structs.XMLElement import XMLElement
from ...parser.types.LibTypes import CriteriaArgument, NestedCriteria
from appium.webdriver.webdriver import WebDriver

from ...util.camel_to_snake import camel_to_snake


class EspressoCriteria:
    @staticmethod
    def all_of(arg: List[CriteriaArgument | NestedCriteria], driver: WebDriver, root: XMLElement):
        funcs = [getattr(EspressoCriteria, camel_to_snake(c["name"]))(c["args"], driver=driver, root=root) for c in arg]

        def f(e: XMLElement) -> bool:
            return all(func(e) for func in funcs)

        return f

    @staticmethod
    # TODO: Revisit this and fromParent, I don't understand these.
    def child_at_position(arg: List[CriteriaArgument | NestedCriteria], driver: WebDriver, root: XMLElement):
        index = arg[1]["content"]
        parent_criteria = arg[0]

        func_name = camel_to_snake(parent_criteria["name"])
        func = getattr(EspressoCriteria, func_name)(parent_criteria["args"], driver=driver, root=root)

        def f(e: XMLElement) -> bool:
            ancestors = e.find_ancestors(lambda elem: True)
            if len(ancestors) == 0:
                return False

            for ancestor in ancestors:
                if func(ancestor) and ancestor.get("index") == index:
                    return True

            return False

        return f

    @staticmethod
    def contains_string_ignoring_case(arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement, referrer: str):
        text = arg[0]["content"]

        def f(e: XMLElement) -> bool:
            if referrer == "with_class_name":
                return text.lower() in e.tag.lower()
            if referrer == "with_text":
                return text.lower() in e.get("text").lower()

        return f

    @staticmethod
    def ends_with_ignoring_case(arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement, referrer: str):
        text = arg[0]["content"]

        def f(e: XMLElement) -> bool:
            if referrer == "with_class_name":
                return e.tag.lower().endswith(text.lower())

        return f

    @staticmethod
    # Special keyword is handled in camel_to_snake
    def _is(arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement, referrer: str):
        text = arg[0]["content"]

        def f(e: XMLElement) -> bool:
            if referrer == "with_class_name":
                return e.tag == text
            if referrer == "with_text":
                return e.get("text") == text

        return f

    @staticmethod
    def is_displayed(_arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement):
        return lambda e: e.get("displayed") == "true"

    @staticmethod
    def is_focused(_arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement):
        return lambda e: e.get("focused") == "true"

    @staticmethod
    def is_not_checked(_arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement):
        def f(e: XMLElement) -> bool:
            checked = e.get("checked")

            if checked is None:
                return False

            return checked == "false"

        return f

    @staticmethod
    def with_class_name(arg: List[CriteriaArgument | NestedCriteria], driver: WebDriver, root: XMLElement):
        matcher = arg[0]

        func_name = camel_to_snake(matcher["name"])
        func = getattr(EspressoCriteria, func_name)(matcher["args"], driver=driver, root=root,
                                                    referrer="with_class_name")

        def f(e: XMLElement) -> bool:
            return func(e)

        return f

    @staticmethod
    def with_content_description(arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement):
        text = arg[0]["content"]

        def f(e: XMLElement) -> bool:
            cd = e.get("content-desc")

            if cd is None:
                return False

            return e.get("content-desc") == text

        return f

    @staticmethod
    def with_hint(arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement):
        text = arg[0]["content"]

        def f(e: XMLElement) -> bool:
            hint = e.get("text")

            if hint is None:
                return False

            return hint == text

        return f

    @staticmethod
    def with_id(arg: List[CriteriaArgument], driver: WebDriver, root: XMLElement):
        id_text = arg[0]["content"]

        def f(e: XMLElement) -> bool:
            rid = e.get("resource-id")

            if rid is None:
                return False

            current_pkg = driver.current_package
            id_format = id_text.split(".")[-1]
            return rid == f"{current_pkg}:id/{id_format}" or rid == f"android:id/{id_format}"

        return f

    @staticmethod
    def with_parent(arg: List[CriteriaArgument | NestedCriteria], driver: WebDriver, root: XMLElement):
        parent_criteria = arg[0]

        func_name = camel_to_snake(parent_criteria["name"])
        func = getattr(EspressoCriteria, func_name)(parent_criteria["args"], driver=driver, root=root)

        def f(e: XMLElement) -> bool:
            if e.get_parent() is None:
                return False

            return func(e.get_parent())

        return f

    @staticmethod
    def with_text(arg: List[CriteriaArgument | NestedCriteria], driver: WebDriver, root: XMLElement):
        if "name" in arg[0]:
            func_name = arg[0]["name"]
            if func_name == "containsString":
                text = arg[0]["args"][0]["content"]

                def f(e: XMLElement) -> bool:
                    return text in e.get("text")

                return f
            elif func_name == "is":
                text = arg[0]["args"][0]["content"]

                def f(e: XMLElement) -> bool:
                    return e.get("text") == text

                return f

        text = arg[0]["content"]

        def f(e: XMLElement) -> bool:
            return e.get("text") == text

        return f
