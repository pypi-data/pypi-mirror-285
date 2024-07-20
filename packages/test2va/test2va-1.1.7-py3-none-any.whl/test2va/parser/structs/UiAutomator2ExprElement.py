from typing import List

from test2va.const.const import NSURL
from test2va.parser.structs.XMLElement import XMLElement
from test2va.parser.types.LibTypes import ActionData, CriteriaData, NestedCriteria, SelectorData, ActionArg, AssertionData, \
    NestedActionArg, CriteriaArgument
from test2va.parser.util.literal_format_check import literal_format_check
from test2va.util.filter_list import filter_list
from test2va.util.map_list import map_list


class UiAutomator2ExprElement(XMLElement):

    def __init__(self, tag: str, attrib: dict = {}, **extra):
        super().__init__(tag, attrib, **extra)
        # This is assigned after this is constructed.
        self._element: XMLElement

    def get_action_data(self) -> ActionData:
        # The call containing the action data is the last child of the expression.
        expr_call_children = filter_list(self._element.get_children(), lambda e: e.tag == f"{{{NSURL}}}call")

        # The action call should be the last sibling call.
        action_call = expr_call_children[-1]

        data: ActionData = {
            "action": action_call.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}name").text,
            "args": []
        }

        # Let's loop through each argument.
        argument_list = action_call.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}argument_list")
        arguments = filter_list(argument_list.get_children(), lambda e: e.tag == f"{{{NSURL}}}argument")
        for arg in arguments:
            expr = arg.find_first_child(lambda e: e.tag == f"{{{NSURL}}}expr")
            # There are a ton of special cases so let's get into it.

            # Case 1: Point
            # Here, actually nothing needs to be done because the x and y data are in literals.
            # They will still be found via literal descendants.

            call = expr.find_first_child(lambda e: e.tag == f"{{{NSURL}}}call")
            if call is not None:
                name = call.find_first_child(lambda e: e.tag == f"{{{NSURL}}}name")
                if name is not None and len(name.get_children()) > 0:

                    # Case 2: Until
                    if name.get_children()[0].text == "Until":
                        until_action = name.get_children()[-1]
                        until_arg_data: ActionArg = {
                            "type": f"Until.{until_action.text}",
                            "content": "",
                            "nested": False
                        }

                        # Until Case 1: Nothing
                        if until_action.text == "newWindow":
                            data["args"].append(until_arg_data)
                            continue

                        # Until Case 2: Direction
                        if until_action.text == "scrollFinished":
                            uac = call.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}argument_list")
                            uac_name = uac.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}name")
                            direction = uac_name.get_children()[-1].text
                            until_arg_data["content"] = direction
                            data["args"].append(until_arg_data)
                            continue

                        # Until Case 3: Pattern - same as literal

                        sel_names = ["findObject", "findObjects", "gone", "hasObject"]
                        # Until Case 4: Selector
                        if until_action.text in sel_names:
                            uia2 = expr.as_uia2()
                            until_arg_data: NestedActionArg = {
                                "type": "UiAutomator2",
                                "criteria": uia2.get_component_data(),
                                "nested": True
                            }
                            data["args"].append(until_arg_data)
                            continue

                        # Until Case 5: Literal
                        until_arg_data["content"] = call.find_first_descendant(
                            lambda e: e.tag == f"{{{NSURL}}}literal").text

                        literal_format_check(until_arg_data)

                        data["args"].append(until_arg_data)

                        continue

            # Case 3: Literal
            # The arguments are literal tags in the call.
            literals = arg.find_descendants(lambda e: e.tag == f"{{{NSURL}}}literal")

            # Case 4: Direction
            if len(literals) == 0:
                expr_name = expr.find_first_child(lambda e: e.tag == f"{{{NSURL}}}name")
                direction = expr_name.get_children()[-1].text
                direction_arg_data: ActionArg = {
                    "type": "Direction",
                    "content": direction,
                    "nested": False
                }

                data["args"].append(direction_arg_data)
            else:
                for literal in literals:
                    # Literal data.
                    literal_data: ActionArg = {
                        "type": literal.get("type"),
                        "content": literal.text,
                        "nested": False
                    }

                    literal_format_check(literal_data)

                    # Adding the literal data to the action arguments.
                    data["args"].append(literal_data)

        return data

    def get_component_data(self) -> List[CriteriaData | NestedCriteria]:
        # First, we want to get the first argument list descendant of the expression.
        arg_list = self._element.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}argument_list")

        data = []

        _component_helper(arg_list, data)

        return data

    def is_in_assertion(self) -> bool:
        # To check if this is a by selector in an assertion, we will check if it
        # is a descendant of a name tag with an immediate name child with text "Assert".
        arr = self._element.find_ancestors(lambda e: e.tag == f"{{{NSURL}}}expr")

        if arr is None or len(arr) == 0:
            return False

        expr = arr[0]

        if expr.find_first_descendant(lambda e: e.text == "Assert") is None:
            return False

        return True

    def get_data(self) -> SelectorData:
        components = self.get_component_data()
        action = self.get_action_data()

        data: SelectorData = {
            "type": "UiAutomator2",
            "criteria": components,
            "action": action,
            "string": None,
            "search_type": None
        }

        return data

    @staticmethod
    def parse_assertion(test_method: XMLElement) -> List[AssertionData]:
        selectors_with_assertion = UiAutomator2ExprElement.find_selector_structures(test_method, False)

        assertion_selectors = filter_list(selectors_with_assertion, lambda e: e.is_in_assertion())

        data: List[AssertionData] = []

        for selector in assertion_selectors:
            expr = selector.find_ancestors(lambda e: e.tag == f"{{{NSURL}}}expr")

            assertion_data: AssertionData = {
                "method": expr.find_first_descendant(lambda e: e.text.startswith("assert")).text,
                "selector": selector.get_data()
            }

            data.append(assertion_data)

        return data

    @staticmethod
    def search_func(test_function_element: XMLElement) -> bool:

        # This will find all expression tags with a descendant name tag with text "findObject".
        if test_function_element.tag != f"{{{NSURL}}}expr":
            return False

        call = test_function_element.find_first_child(lambda e: e.tag == f"{{{NSURL}}}call")

        if call is None:
            return False

        name = call.find_first_child(lambda e: e.tag == f"{{{NSURL}}}name")

        if name is None:
            return False

        if name.find_first_child(lambda e: e.text == "findObject") is None:
            return False

        return True

    @staticmethod
    def find_selector_structures(test_function_element: XMLElement, filter_assertion=True) -> List[
        "UiAutomator2ExprElement"]:
        expr = test_function_element.find_descendants(UiAutomator2ExprElement.search_func)
        to_expr: List["UiAutomator2ExprElement"] = map_list(expr, lambda e: e.as_uia2())

        if filter_assertion:
            no_assert = filter_list(to_expr, lambda e: not e.is_in_assertion())
            return no_assert

        return to_expr


def _component_helper(arg_list: XMLElement, data: List[CriteriaData | NestedCriteria | CriteriaArgument]):
    # First, let's get all arguments in the argument list.
    args = filter_list(arg_list.get_children(), lambda e: e.tag == f"{{{NSURL}}}argument")

    # Now, lets determine in there are nested components.
    # If there are then it may mean this is the argument representing the entire selector.
    # It could also mean we are in a nested component.
    # To do that, let's loop through each argument.

    for arg in args:
        arg_expr = arg.find_first_child(lambda e: e.tag == f"{{{NSURL}}}expr")

        # Now we are going to check if the argument expression has a direct call child. If it does, then this
        # is a nested in some way as described above.
        arg_expr_calls = filter_list(arg_expr.get_children(), lambda e: e.tag == f"{{{NSURL}}}call")

        # Dealing with nesting
        if len(arg_expr_calls) > 0:

            for arg_expr_call in arg_expr_calls:

                nested_name = arg_expr_call.find_first_child(lambda e: e.tag == f"{{{NSURL}}}name")
                # There are two forms of nesting, this is one way to get the name.
                nested_data: NestedCriteria = {
                    "name": nested_name.text,
                    "criteria": [],
                    "nested": True
                }

                # If this name is empty, then we will get the children of that name tag and find the last child name.
                if nested_data["name"] == "":
                    nested_name = filter_list(nested_name.get_children(), lambda e: e.tag == f"{{{NSURL}}}name")[
                        -1]
                    nested_data["name"] = nested_name.text

                # There is one special parsing case for UiAutomator2 Components.
                # That is using Pattern.compile().
                # So, if the current name is "compile", then we will execute this special case.
                if nested_data["name"] == "compile":
                    compile_case_data: CriteriaArgument = {
                        "type": "pattern",
                        "content": (arg_expr_call.find_first_descendant(
                            lambda e: e.tag == f"{{{NSURL}}}literal").text)[1:-1]
                    }

                    data.append(compile_case_data)
                    continue

                # If it isn't the special case, we can recurse.
                _component_helper(arg_expr_call.find_first_child(lambda e: e.tag == f"{{{NSURL}}}argument_list"),
                                  nested_data["criteria"])

                data.append(nested_data)

        else:
            # If it isn't nested, then there must be a literal.
            arg_expr_literal = arg_expr.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}literal")

            # There is one special case in the clazz component.
            # There won't be a literal, so first we will check if the literal is none.
            if arg_expr_literal is None:
                expr_name = arg_expr.find_first_child(lambda e: e.tag == f"{{{NSURL}}}name")
                # The string will be created by getting all children of the name and concatenating their texts.

                literal_data: CriteriaArgument = {
                    "type": "string",
                    "content": "".join(map_list(expr_name.get_children(), lambda e: e.text))
                }
            else:

                literal_data: CriteriaArgument = {
                    "type": arg_expr_literal.get("type"),
                    "content": arg_expr_literal.text
                }

                literal_format_check(literal_data)

            data.append(literal_data)
