from typing import List, Literal

from test2va.const.const import NSURL
from test2va.parser.structs.XMLElement import XMLElement
from test2va.parser.types.LibTypes import ActionData, CriteriaData, NestedCriteria, SelectorData, ActionArg, AssertionData, \
    NestedActionArg, CriteriaArgument
from test2va.parser.util.literal_format_check import literal_format_check
from test2va.util.filter_list import filter_list
from test2va.util.map_list import map_list


class EspressoDeclElement(XMLElement):

    def __init__(self, tag: str, attrib: dict = {}, **extra):
        super().__init__(tag, attrib, **extra)
        # This is assigned after this is constructed.
        self._element: XMLElement

    def get_data(self) -> SelectorData:
        data: SelectorData = {
            "type": "Espresso",
            "criteria": self.get_search_criteria(),
            "action": self.get_action_data(),
            "string": None,
            "search_type": self.get_search_type()
        }

        return data

    def get_search_criteria(self) -> List[CriteriaData | NestedCriteria]:
        # To get the search criteria, we need to find the second descendant that is a call tag.
        # This is the same first step for getting the search type.
        call_tag = self._element.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}call")
        lower_call_tag = call_tag.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}call")
        arg_list = lower_call_tag.find_first_child(lambda elem: elem.tag == f"{{{NSURL}}}argument_list")

        data = []
        get_criteria_data(arg_list, data)

        return data

    def get_var_name(self) -> str:
        # The name of the variable storing the view interaction is the text of the first child that is a name tag.
        name_tag = self._element.find_first_child(lambda elem: elem.tag == f"{{{NSURL}}}name")
        if name_tag is not None:
            return name_tag.text

        return ""

    def get_search_type(self) -> Literal["allOf", "anyOf", "is", "not", "endsWith", "startsWith", "instanceOf"]:
        # To find the type of search being performed, we need to find the first descendant that is a call tag.
        # Then, we will find the first descendant of that descendant that is also a call tag.
        # Finally, the search type is the text of the first name tag of that child.
        call_tag = self._element.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}call")
        lower_call_tag = call_tag.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}call")
        name_tag = lower_call_tag.find_first_child(lambda elem: elem.tag == f"{{{NSURL}}}name")

        return name_tag.text

    def get_action_data(self) -> ActionData:
        data: ActionData = {
            "action": "",
            "args": []
        }

        # To check if the view interaction is an assertion, we need to locate where the variable storing it is being
        # used. To do this, we are going to find the root of the tree so the descendants can be searched for uses.
        # TODO: This causes an issue if there are duplicate selector names, such as one a "before" function.
        root = self._element.find_ancestors(lambda e: True)[-1]
        # Now we are going to search all name tags with text equal to the text of the variable storing the interaction.
        root_name_tags = root.find_descendants(
            lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == self.get_var_name())
        if len(root_name_tags) == 0:
            return data
        # Now we are going to check each use of the variable to see if an action is being performed on it.
        # We will check the following criteria:
        # 1. The variable's parent is a name tag.
        # 2. The variable's parent has a child that is an "operator" tag with text equal to ".".
        # 3. The variable's parent has a child that is a "name" tag with text equal to "perform".
        parent = None
        for name_tags in root_name_tags:
            parent = name_tags.get_parent()
            if parent is None:
                continue

            if parent.tag != f"{{{NSURL}}}name":
                continue

            operator_tag = parent.find_first_child(
                lambda elem: elem.tag == f"{{{NSURL}}}operator" and elem.text == ".")
            if operator_tag is None:
                continue

            name_tag = parent.find_first_child(
                lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == "perform")
            if name_tag is None:
                continue

            break

        if parent is None:
            return data

        # Next, we want to find the first sibling of the parent that is an "argument_list" tag.
        siblings = parent.get_siblings()
        arg_list = None
        for sibling in siblings:
            if sibling.tag == f"{{{NSURL}}}argument_list":
                arg_list = sibling
                break

        if arg_list is None:
            return data

        # Now that the argument list has been found, we want to find the first descendant that is a call tag.
        call_tag = arg_list.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}call")
        if call_tag is None:
            return data

        # The action name is in the first name child of the call tag.
        data["action"] = call_tag.find_first_child(lambda elem: elem.tag == f"{{{NSURL}}}name").text

        # There is a special case if the action is pressKey(EspressoKey).
        # To check if the special case should execute, we will first check if the action name is "pressKey"
        # and also check if the call tag has a descendant that is an operator tag with the text "new".

        if data["action"] == "pressKey" and call_tag.find_first_descendant(
                lambda elem: elem.tag == f"{{{NSURL}}}operator" and elem.text == "new") is not None:
            # Now we will check for each aspect of this builder.
            with_alt_pressed = call_tag.find_first_descendant(
                lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == "withAltPressed")
            with_ctrl_pressed = call_tag.find_first_descendant(
                lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == "withCtrlPressed")
            with_shift_pressed = call_tag.find_first_descendant(
                lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == "withShiftPressed")
            with_key_code = call_tag.find_first_descendant(
                lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == "withKeyCode")

            # For each of these vars, we will check if they aren't none then find the text inside their literal tag.
            # If they exist, add them to data["args"] with type as their var name and the data as the literal content.
            if with_alt_pressed is not None:
                action_arg: ActionArg = {
                    "type": "withAltPressed",
                    "content": with_alt_pressed.get_parent().find_first_descendant(
                        lambda elem: elem.tag == f"{{{NSURL}}}literal").text,
                    "nested": False
                }
                data["args"].append(action_arg)
            if with_ctrl_pressed is not None:
                action_arg: ActionArg = {
                    "type": "withCtrlPressed",
                    "content": with_ctrl_pressed.get_parent().find_first_descendant(
                        lambda elem: elem.tag == f"{{{NSURL}}}literal").text,
                    "nested": False
                }
                data["args"].append(action_arg)
            if with_shift_pressed is not None:
                action_arg: ActionArg = {
                    "type": "withShiftPressed",
                    "content": with_shift_pressed.get_parent().find_first_descendant(
                        lambda elem: elem.tag == f"{{{NSURL}}}literal").text,
                    "nested": False
                }
                data["args"].append(action_arg)
            if with_key_code is not None:
                action_arg: ActionArg = {
                    "type": "withKeyCode",
                    "content": with_key_code.get_parent().find_first_descendant(
                        lambda elem: elem.tag == f"{{{NSURL}}}literal").text,
                    "nested": False
                }
                data["args"].append(action_arg)
        else:
            call_arg_list = call_tag.find_first_child(lambda elem: elem.tag == f"{{{NSURL}}}argument_list")
            get_criteria_data(call_arg_list, data["args"])

        return data

    def is_assertion(self) -> bool:
        # To check if the view interaction is an assertion, we need to locate where the variable storing it is being
        # used. To do this, we are going to find the root of the tree so the descendants can be searched for uses.
        root = self._element.find_ancestors(lambda e: True)[-1]
        # Now we are going to search all name tags with text equal to the text of the variable storing the interaction.
        root_name_tags = root.find_descendants(
            lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == self.get_var_name())
        if len(root_name_tags) == 0:
            return False
        # Now we are going to check each use of the variable to see if it is an assertion.
        # We will check if it has two siblings matching the following criteria respectively:
        # 1. A sibling that is an "operator" tag with text "."
        # 2. A sibling that is a "name" tag with text "check"
        # If both of these are true, then the view interaction is an assertion.
        for name_tag in root_name_tags:
            siblings = name_tag.get_siblings()
            if len(siblings) < 2:
                continue

            # I should have made a method with a callback filter for siblings :/
            operator = filter_list(siblings,
                                   lambda sibling: sibling.tag == f"{{{NSURL}}}operator" and sibling.text == ".")
            if len(operator) == 0:
                continue

            name = filter_list(siblings,
                               lambda sibling: sibling.tag == f"{{{NSURL}}}name" and sibling.text == "check")
            if len(name) == 0:
                continue

            return True

        return False

    @staticmethod
    def parse_assertion(test_method: XMLElement) -> List[AssertionData]:
        selectors_with_assertion = EspressoDeclElement.find_selector_structures(test_method, False)

        assertion_selectors = filter_list(selectors_with_assertion, lambda e: e.is_assertion())

        data = []

        for selector in assertion_selectors:
            # expr = assertion_selector.find_ancestors(lambda e: e.tag == f"{{{NSURL}}}expr")

            assertion_data: AssertionData = {
                "method": None,
                "selector": selector.get_data()
            }

            data.append(assertion_data)

        return data

    @staticmethod
    def search_func(test_function_element: XMLElement) -> bool:
        # We want to find a descendant of the test function that is a decl tag
        # that has an immediate child that is a type tag
        # and that type tag have an immediate child that is a name tag with text "ViewInteraction".
        if test_function_element.tag != f"{{{NSURL}}}decl":
            return False

        type_tag = test_function_element.find_first_child(lambda elem: elem.tag == f"{{{NSURL}}}type")
        if type_tag is None:
            return False

        name = type_tag.find_first_child(
            lambda elem: elem.tag == f"{{{NSURL}}}name" and elem.text == "ViewInteraction")
        if name is None:
            return False

        return True

    @staticmethod
    def find_selector_structures(test_function_element: XMLElement, filter_assertion=True) -> List[
        "EspressoDeclElement"]:
        decls = test_function_element.find_descendants(EspressoDeclElement.search_func)
        to_decl = map_list(decls, lambda e: e.as_espresso_decl())

        if filter_assertion:
            no_assert = filter_list(to_decl, lambda e: not e.is_assertion())
            return no_assert

        return to_decl


def get_criteria_data(arg_list: XMLElement,
                      args: List[CriteriaData | NestedCriteria] | List[ActionArg | NestedActionArg] | List[
                          CriteriaArgument], prev: CriteriaData = None):
    arguments = arg_list.find_descendants(lambda elem: elem.tag == f"{{{NSURL}}}argument")
    filtered: List[XMLElement] = filter_list(arguments, lambda e: e.depth() == arguments[0].depth())

    for argument in filtered:
        nested_arg = argument.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}argument_list")
        if nested_arg is not None:
            if prev is not None:
                prev["nested"] = True
            # Special case with example IsInstanceOf.<View>instanceOf
            # Instead of being the first name descendant, the complex type will be the first name child of the first
            # call descendant.
            # We can check for the case by seeing if the default search results in an empty text string.
            data: CriteriaData = {
                "name": argument.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}name").text,
                "args": [],
                "nested": False,
            }

            if data["name"] == "":
                call = argument.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}call")
                data["name"] = call.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}name").text

            # Special Case with example ViewMatchers.Visibility.valueOf()
            # If it is still an empty string, then we will first get the first name descendant.
            # Then the result is the combination of the texts of all of its children.
            if data["name"] == "":
                name = argument.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}name")
                name_children = name.get_children()
                string = ""

                for child in name_children:
                    string += child.text

                data["name"] = string

            get_criteria_data(nested_arg, data["args"], data)
            args.append(data)
            continue

        literal: XMLElement = argument.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}literal")
        if literal is not None:
            data: CriteriaArgument = {
                "type": literal.get("type"),
                "content": literal.text
            }

            literal_format_check(data)
        else:
            # This is either something like R.id.<name> or maybe a variable reference.
            # Let's check for the ref first.
            arg_name = argument.find_first_descendant(lambda elem: elem.tag == f"{{{NSURL}}}name")

            # Getting root
            if arg_name.text is not None:
                root = arg_name.find_ancestors(lambda e: True)[-1]
                names = root.find_descendants(
                    lambda e: e.tag == f"{{{NSURL}}}name" and e.index() < arg_name.index() and e.text == arg_name.text)
                init_names = filter_list(names, lambda e: len(
                    filter_list(e.get_siblings(), lambda ele: ele.tag == f"{{{NSURL}}}init")) > 0)
                if len(init_names) > 0:
                    lit = init_names[-1].get_parent().find_first_descendant(lambda e: e.tag == f"{{{NSURL}}}literal")
                    if lit is not None:
                        data: CriteriaArgument = {
                            "type": lit.get("type"),
                            "content": lit.text
                        }
                        literal_format_check(data)
                        args.append(data)
                        continue

            name_children = arg_name.get_children()
            string = ""

            for child in name_children:
                string += child.text

            data: CriteriaArgument = {
                "type": "string",
                "content": string
            }

        args.append(data)
