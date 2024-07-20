from typing import List

from test2va.const.const import NSURL
from test2va.parser.structs.XMLElement import XMLElement
from test2va.parser.types.LibTypes import ActionData, CriteriaArgument, CriteriaData, NestedCriteria, SelectorData, ActionArg, AssertionData
from test2va.parser.util.literal_format_check import literal_format_check
from test2va.util.filter_list import filter_list
from test2va.util.map_list import map_list

UIS1_NESTED_SELECTOR_NAMES = ["childSelector", "fromParent"]


class UiAutomator1ExprElement(XMLElement):

    def __init__(self, tag: str, attrib: dict = {}, **extra):
        super().__init__(tag, attrib, **extra)
        # This is assigned after this is constructed.
        self._element: XMLElement

    def get_action_data(self) -> ActionData:
        # The action data should be housed in the last child call of the selector expression.
        expr_call_children = filter_list(self._element.get_children(), lambda e: e.tag == f"{{{NSURL}}}call")

        # The action call should be the last sibling call.
        action_call = expr_call_children[-1]

        # The action name is in the first name child of the call.
        action_data: ActionData = {
            "action": action_call.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}name").text,
            "args": []
        }

        # Special Action Case: dragTo (with UiSelector arg)
        if action_data["action"] == "drag_to" and action_call.find_first_descendant(
                UiAutomator1ExprElement.search_func) is not None:
            _parse_drag_to_action(action_call, action_data)
        elif action_data["action"] == "perform_two_pointer_gesture":
            _parse_perform_two_pointer_gesture_action(action_call, action_data)
        elif action_data["action"] == "perform_multi_pointer_gesture":
            _parse_perform_multi_pointer_gesture_action(action_call, action_data)
        else:
            # The arguments are literal tags in the call.
            literals = action_call.find_descendants(lambda e: e.tag == f"{{{NSURL}}}literal")

            for literal in literals:
                # Literal data.
                literal_data: ActionArg = {
                    "type": literal.get("type"),
                    "content": literal.text,
                    "nested": False
                }

                # Checking for literal parsing cases.
                literal_format_check(literal_data)

                # Adding the literal data to the action arguments.
                action_data["args"].append(literal_data)

        return action_data

    def get_component_data(self) -> List[CriteriaData | NestedCriteria]:
        data = []

        # First we will get the UiSelector call from the expression.
        call = self._element.find_first_descendant(self.search_func).find_first_ancestor(
            lambda e: e.tag == f"{{{NSURL}}}call")

        # We will get the siblings of the call.
        siblings = call.get_siblings()

        # We will filter output the siblings that are not calls.
        sibling_calls = filter_list(siblings, lambda e: e.tag == f"{{{NSURL}}}call")

        # If for some reason there aren't any sibling calls, we will return an empty array.
        if len(sibling_calls) == 0:
            return data

        for component_call in sibling_calls:
            # Adding the component data to the selector data.
            data.append(_get_component_data(component_call))

        return data

    def get_data(self) -> SelectorData:
        components = self.get_component_data()
        action = self.get_action_data()

        data: SelectorData = {
            "type": "UiAutomator1",
            "criteria": components,
            "action": action,
            "string": _selector_to_string(components),
            "search_type": None,
        }

        return data

    @staticmethod
    def parse_assertion(test_method: XMLElement) -> List[AssertionData]:
        # We will find a name tag with text "Assert".
        assertion_name = test_method.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}name" and e.text == "Assert")

        # We will get the type of the assertion by finding the last sibling of the name.
        assertion_type = filter_list(assertion_name.get_siblings(), lambda e: e.tag == f"{{{NSURL}}}name")[-1].text

        # Now we will get the assertion call.
        assertion_call = assertion_name.find_first_ancestor(lambda e: e.tag == f"{{{NSURL}}}call")

        # From there we will get the selector in the assertion.
        assertion_selector = assertion_call.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}expr")

        assertion_data: AssertionData = {
            "method": assertion_type,
            "selector": assertion_selector.as_uis1().get_data()
        }

        return [assertion_data]

    @staticmethod
    def search_func(test_function_element: XMLElement) -> bool:
        return (
                test_function_element.tag == f"{{{NSURL}}}name" and
                test_function_element.text is not None and
                test_function_element.text.strip().lower() == "uiselector"
        )

    # Finds all un-nested selector expressions.
    # The expression tag contains the selector component data and the action data.
    @staticmethod
    def find_selector_structures(test_function_element: XMLElement) -> List["UiAutomator1ExprElement"]:
        # To find UiSelectors, we find all "name" tags with text "UiSelector".
        selectors = test_function_element.find_descendants(UiAutomator1ExprElement.search_func)

        if len(selectors) == 0:
            return []

        # Now that the UiSelectors are found, we have to differentiate between those that are nested
        # and those that are not.
        # Most likely, the first UiSelector in the list will be the guide for those that are not nested.
        # So, we will filter output the selectors with depths different from the first selector.
        un_nested = filter_list(selectors, lambda e: e.depth() == selectors[0].depth())

        # Now that all the un-nested selectors are found, we can find the expression containing the selector call
        # and action call.
        # To that we will find the first argument_list tag above the selector call.
        # Then we will find the first expr tag above that.
        selector_argument_lists = map_list(un_nested, lambda e: e.find_first_ancestor(
            lambda ele: ele.tag == f"{{{NSURL}}}argument_list"))
        selector_expressions = map_list(selector_argument_lists,
                                        lambda e: e.find_first_ancestor(lambda ele: ele.tag == f"{{{NSURL}}}expr"))

        return map_list(selector_expressions, lambda e: e.as_uis1())


def _get_component_data(call: XMLElement) -> CriteriaData | NestedCriteria:
    # The name of the component is in the first name child of the call.
    name = call.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}name").text

    # If the name of the component is in the nested selector names, then it is a nested selector.
    if name in UIS1_NESTED_SELECTOR_NAMES:
        data: NestedCriteria = {
            "name": name,
            "criteria": [],
            "nested": True
        }

        uis_call = call.find_first_descendant(UiAutomator1ExprElement.search_func).find_first_ancestor(
            lambda e: e.tag == f"{{{NSURL}}}call")
        sibling_calls = filter_list(uis_call.get_siblings(), lambda e: e.tag == f"{{{NSURL}}}call")

        for comp_call in sibling_calls:
            data["criteria"].append(_get_component_data(comp_call))

        return data
    else:
        data: CriteriaData = {
            "name": name,
            "args": [],
            "nested": False
        }
        # The arguments are literal tags in the call.
        literals = call.find_descendants(lambda e: e.tag == f"{{{NSURL}}}literal")

        # The literals need to be filtered, however so that nested ones are not included.
        # To do this, we are going to check if the literals depth is similar to the calls.
        filtered_literals = filter_list(literals, lambda e: abs(call.depth() - e.depth()) < 5)

        for literal in filtered_literals:
            # Literal data.
            literal_data: CriteriaArgument = {
                "type": literal.get("type"),
                "content": literal.text
            }

            literal_format_check(literal_data)

            # Adding the literal data to the component data.
            data["args"].append(literal_data)

    return data


def _parse_drag_to_action(action_call: XMLElement, data: ActionData):
    # The other drag_to will parse normally, this is the case if there is a UiSelector arg.

    # From here, we want to form a dummy data structure that represents the UiSelector1 data.
    # The process should mimic what was done above.
    # We can take this data and stringify the UiSelector1 dummy data and use that as the first argument to be used.

    # The UiSelector1 data.
    selector_data = {
        "components": [],
    }

    # The UiSelector1 call.
    selector_call = action_call.find_first_descendant(UiAutomator1ExprElement.search_func).find_first_ancestor(
        lambda e: e.tag == f"{{{NSURL}}}call")
    sibling_calls = filter_list(selector_call.get_siblings(), lambda e: e.tag == f"{{{NSURL}}}call")

    for comp_call in sibling_calls:
        selector_data["components"].append(_get_component_data(comp_call))

    # Stringify the UiSelector1 data.
    selector_string = _selector_to_string(selector_data["components"])

    first_dragto_arg = {
        "type": "string",
        "content": selector_string,
        "nested": False
    }

    # Adding the first argument to the action arguments.
    data["args"].append(first_dragto_arg)

    # The next arg is steps.
    # To get this arg, we can find all literals under the action call, but take the one with the smallest depth.
    literals = action_call.find_descendants(lambda e: e.tag == f"{{{NSURL}}}literal")
    literals_depths = [literal.depth() for literal in literals]
    min_depth = min(literals_depths)
    min_depth_index = literals_depths.index(min_depth)
    steps_literal = literals[min_depth_index]

    # Literal data.
    steps_literal_data = {
        "type": "number",
        "content": steps_literal.text,
        "nested": False
    }

    literal_format_check(steps_literal_data)

    # Adding the steps literal data to the action arguments.
    data["args"].append(steps_literal_data)


def _parse_perform_two_pointer_gesture_action(action_call: XMLElement, data: ActionData):
    # PerformTwoPointerGesture takes 4 Point classes as arguments and then a steps argument.
    # To find the point data, we will find all "name" tags with text "Point" under the call.
    # Then we will find the first ancestor call of each of these.
    # Then we will find all descendant literals of each of these. There should be 2: an x point and a y point.
    # These will be stored as type: "point" and content: {x: x, y: y}.
    # The steps argument will be the same as above.

    point_name_tags = action_call.find_descendants(lambda e: e.tag == f"{{{NSURL}}}name" and e.text == "Point")
    point_calls = [point_name_tag.find_first_ancestor(lambda e: e.tag == f"{{{NSURL}}}call") for point_name_tag
                   in
                   point_name_tags]

    for point_call in point_calls:
        point_literals = point_call.find_descendants(lambda e: e.tag == f"{{{NSURL}}}literal")

        # The point data.
        point_data = {
            "type": "point",
            # Format: "x,y"
            "content": f"{point_literals[0].text},{point_literals[1].text}",
            "nested": False
        }

        # Adding the point data to the action arguments.
        data["args"].append(point_data)

    # The steps argument is the same as above.
    literals = action_call.find_descendants(lambda e: e.tag == f"{{{NSURL}}}literal")
    literals_depths = [literal.depth() for literal in literals]
    min_depth = min(literals_depths)
    min_depth_index = literals_depths.index(min_depth)
    steps_literal = literals[min_depth_index]

    # Literal data.
    steps_literal_data = {
        "type": "number",
        "content": steps_literal.text,
        "nested": False
    }

    literal_format_check(steps_literal_data)

    # Adding the steps literal data to the action arguments.
    data["args"].append(steps_literal_data)


def _parse_perform_multi_pointer_gesture_action(action_call: XMLElement, data: ActionData):
    # This one is a bit tricky because it can take on different forms.
    # This structure is how I am basing the parsing off of:
    """
        PointerCoords p1 = new PointerCoords();
        p1.x = 5;
        p1.y = 5;
        p1.pressure = 1;
        p1.size = 1;

        PointerCoords p2 = new PointerCoords();
        p2.x = 10;
        p2.y = 10;
        p2.pressure = 1;
        p2.size = 1;

        device.getObject(
                new UiSelector().resourceId("com.android.settings:id/main_content_scrollable_container"),
                2000
        ).performMultiPointerGesture(
                new MotionEvent.PointerCoords[][]{
                        {p1, p2}
                }
        );
    """

    # First, we want to find a descendant that is a block under the action call,
    block = action_call.find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}block")

    # From here, we want to get all descendants that are name tags. These are the vars that represent the pointer
    # cords.
    name_tags = block.find_descendants(lambda e: e.tag == f"{{{NSURL}}}name")

    # Then, we want to find the root element, so we can look for these vars.
    root = action_call.find_ancestors(lambda e: True)[-1]

    for name_tag in name_tags:
        # We want to find all descendants of the root that are name tags and have the text of each var,
        # But also have a different depth than the original.
        # And also have a sibling that is an operator with text ".".
        usage = root.find_descendants(
            lambda e:
            e.tag == f"{{{NSURL}}}name" and
            e.text == name_tag.text and e.depth() != name_tag.depth() and
            len(filter_list(e.get_siblings(), lambda s: s.tag == f"{{{NSURL}}}operator" and s.text == ".")) > 0
        )

        pc_data = {
            "type": "pointerCoords",
            "content": {}
        }

        # For each time that the var is used, the attribute is found by finding the first name tag sibling,
        # and the value is found by finding the first literal tag sibling of the first name ancestor.
        for use in usage:
            attribute = filter_list(use.get_siblings(), lambda e: e.tag == f"{{{NSURL}}}name")[0]
            temp = attribute.find_first_ancestor(lambda e: e.tag == f"{{{NSURL}}}name")
            value = filter_list(temp.get_siblings(), lambda e: e.tag == f"{{{NSURL}}}literal")[0]

            pc_data["content"][attribute.text] = value.text

        data["args"].append(pc_data)


def _selector_to_string(components: list[CriteriaData | NestedCriteria]):
    selector = "new UiSelector()"
    for comp in components:
        if "criteria" in comp:
            selector += f".{comp['name']}({_selector_to_string(comp['criteria'])})"
        else:
            args = [arg["content"] if arg["type"] != "string" else f'"{arg["content"]}"' for arg in comp["args"]]
            selector += f".{comp['name']}({', '.join(args)})"
    return selector
