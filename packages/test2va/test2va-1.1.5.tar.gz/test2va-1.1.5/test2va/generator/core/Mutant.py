import json
from typing import Tuple

from test2va.generator.core import GUIMethodReader
from test2va.generator.core.GUI import GUIElement, GUIEvent, GUIControl


class MutantException(Exception):
    def __init__(self, message):
        super().__init__(message)


class MutantInfoPerEvent:
    """
    This class represent the original event and its related mutant events information
    Note: each obj only contains one original event
    """
    _input_mutant_parameter: tuple[str, str, str]

    def __init__(self, mutant_result_file_path: str, event: GUIEvent, index: int):
        """
        The constructor is used to collect the mutant information for an event
        :param mutant_result_file_path:
        :param event:
        :param index:
        """

        self._mutant_replaceable_elements = []
        self._original_event = event
        self._event_index = index
        self._mutant_replaceable_events = []
        self._click_mutant_parameters = []
        self._input_mutant_parameter = ('', '', '')

        # initialize json data
        with open(mutant_result_file_path, 'r') as file:
            self._json_data = json.load(file)

        if self.is_mutable_event():
            self._set_mutant_replaceable_elements()
            self._set_mutant_replaceable_events()
            self._set_parameters()

    def is_mutable_event(self):
        """
        return true if the event is a mutable event
        :return:
        """
        if str(self._event_index) in self._json_data:
            return self._json_data[str(self._event_index)]['mutable']
        else:
            raise MutantException("The illegal event index value: " + str(self._event_index))

    def get_mutant_replaceable_events(self):
        """
        This method will return a list of replaceable events of the target original event
        :return:
        """
        return self._mutant_replaceable_events

    def _set_mutant_replaceable_elements(self):
        """
        This method is used to set up the mutant elements of given index

        mutant_elements = [element 1, element 2]
        :return:
        """

        # index not exist
        if str(self._event_index) not in self._json_data:
            raise MutantException("index not exist in mutant result file: " + str(self._event_index))

        # successful_path is empty
        if not self._json_data[str(self._event_index)]['successful_paths']:
            raise MutantException("successful_path with index " + str(self._event_index) +
                                  " is empty, please check detector algorithm.")

        # find successful_paths
        successful_paths = self._json_data[str(self._event_index)]['successful_paths']

        # put all the detected mutant replaceable elements in the mutant_element_list
        # mutant_element_num = len(successful_paths)
        # mutant_count = 0
        # while mutant_count < mutant_element_num:
        #     mutant_replaceable_element: GUIElement = GUIMethodReader.update_element(
        #         successful_paths[mutant_count][self._event_index])
        #     self._mutant_replaceable_elements.append(mutant_replaceable_element)
        #     mutant_count += 1

        # put all the detected mutant replaceable elements in the mutant_element_list
        for successful_path in successful_paths:
            if successful_path:
                mutant_replaceable_element: GUIElement = GUIMethodReader.update_element(
                    successful_path[self._event_index])
                self._mutant_replaceable_elements.append(mutant_replaceable_element)

    def _set_mutant_replaceable_events(self):
        """
        This method will create the replaceable events based on the original action and new element
        This list should include the original event

        for input action, remove the input value in original action
        for click action, follow the same action
        :return:
        """

        if self.is_input_event():
            self._mutant_replaceable_events.append(self._original_event)

        elif self.is_click_event():
            # add original event
            self._mutant_replaceable_events.append(self._original_event)
            # add replaceable event
            replaceable_control: GUIControl = self._original_event.get_gui_control()
            for replaceable_element in self._mutant_replaceable_elements:
                replaceable_event: GUIEvent = GUIEvent({}, replaceable_control, replaceable_element)
                self._mutant_replaceable_events.append(replaceable_event)

        else:
            raise MutantException("feature name is not supported: " +
                                  self._original_event.get_gui_control().get_control_feature('name'))

    def _set_parameters(self):
        """
        This method will set the three features of parameters for the event:
            three element tuple, (name, identifier, instance), for example, ('param1', 'text', 'OK')
        - name: "param" + index
        - identifier: follow by the order of 'text', 'content-desc', 'resource-id', choose the first one that
                      are non-empty among all elements (original elements and mutant elements)
        - instance: the value of the identifier

        Note: click event will set up _click_mutant_parameters
              input event will set up _input_mutant_parameter
              no parameter of original event
        :return:
        """
        # parameter name
        name = 'param' + str(self._event_index)

        if self.is_input_event():
            self._input_mutant_parameter = (name, '', '')
        elif self.is_click_event():
            # add mutant parameter of original element
            identifier = self._find_joint_identifiers()
            original_element = self._original_event.get_gui_element()
            self._click_mutant_parameters.append([name, identifier,
                                                  original_element.get_feature_by_name(identifier)])

            # add mutant parameter of replaceable element
            for replaceable_element in self._mutant_replaceable_elements:
                self._click_mutant_parameters.append([name, identifier,
                                                      replaceable_element.get_feature_by_name(identifier)])

    def _find_joint_identifiers(self):
        """
        Use the original element prior id as mutual identifier
        :return:
        """
        identifier = self._original_event.get_gui_element().get_prior_id()
        if identifier:
            return identifier
        else:
            raise MutantException("no joint non empty identifier has been found")

    def is_input_event(self):
        action = self._original_event.get_gui_control()
        return action.get_control_feature('name') == 'replaceText' or action.get_control_feature('name') == 'typeText'

    def is_click_event(self):
        action = self._original_event.get_gui_control()
        return action.get_control_feature('name') == 'click'

    def get_input_mutant_parameter(self):
        if self.is_input_event():
            return self._input_mutant_parameter
        else:
            return None

    def get_click_mutant_parameter_by_index(self, index):
        if 0 <= index < len(self._click_mutant_parameters):
            return self._click_mutant_parameters[index]
        else:
            raise  MutantException("index out of scope: " + str(index))
