from test2va.generator.core.GUI import GUIEvent, GUIMethod
from test2va.generator.exceptions.MethodException import MethodException
from queue import Queue

TEXT_IDENTIFIER_CONSTANT = 'text'
CD_IDENTIFIER_CONSTANT = 'content-desc'
TAB_CONSTANT = "    "
END_OF_STATEMENT_CONSTANT = ";\n"


class Statement:
    """

    """

    def __init__(self, event: GUIEvent, mutant_flag: bool = None, parameter: tuple = None):
        """

        :param event:
        :param mutant_flag:
        :param parameter: three element tuple, (name, identifier, instance), for example, ('param1', 'text', 'OK')
        """
        self._event: GUIEvent = event
        self._identifiers_value_tuple = self.get_all_identifiers_value(event)
        self._mutant_flag = mutant_flag if mutant_flag is not None else False
        self._parameter = parameter if parameter is not None else ('', '', '')

    def get_all_identifiers_value(self, event: GUIEvent):
        """
        The qualified identifiers combo will be:
            - text; text + id
            - content-desc; content-desc + id
            - id
        The method will scan the element in event, and return a list of identifiers
        Please not some of the identifiers may be empty or None

        :param event: GUIEvent
        :return: (text, content_desc, resource_id)
        """

        if event is not None:
            text, content_desc, resource_id = event.get_gui_element().get_identifiers()
            id_tuple = (text, content_desc, resource_id)
            return id_tuple
        else:
            raise MethodException("Cannot get identifiers from an GUI event obj that is None")

    def is_input_event(self):
        action = self._event.get_gui_control()
        return action.get_control_feature('name') == 'replaceText' or action.get_control_feature('name') == 'typeText'

    def is_click_event(self):
        action = self._event.get_gui_control()
        return action.get_control_feature('name') == 'click'

    def is_back_event(self):
        action = self._event.get_gui_control()
        return action.get_control_feature('name') == 'closeSoftKeyboard'

    def is_ime_enter_event(self):
        action = self._event.get_gui_control()
        return action.get_control_feature('name') == 'pressImeActionButton'

    def is_long_click_event(self):
        action = self._event.get_gui_control()
        return action.get_control_feature('name') == 'longClick'


    def to_code(self, language: str):
        """
        Return the string version of statement in specified language
        Now only support java

        static input event example: onEventInputByResourceId("id/label_input", "meeting");
        parameterized input event example: onEventInputByResourceId("id/label_input", param2);

        static click event example:
            onEventClickingByText("Delete", "id/text1");
        static click event example:
            if (param3 = "Delete")
                onEventClickingByText("Delete", "id/text1");

        :param language: str
        :return: a string format of statement
        """
        if language.lower() != 'java':
            raise MethodException("target language is not supported when generating statement in code: " +
                                  language)

        statement = ''

        # 1. the statement is a static event with no parameter
        if not self._mutant_flag:
            # event is an input
            if self.is_input_event():
                api_id_type = self.get_api_id_type()
                statement += (f"{TAB_CONSTANT}onEventInputBy{api_id_type}({self.get_api_id_values(api_id_type)}, "
                              f"{self.get_input_value()})")
                statement += END_OF_STATEMENT_CONSTANT
            # event is a click
            elif self.is_click_event():
                api_id_type = self.get_api_id_type()
                statement += f"{TAB_CONSTANT}onEventClickingBy{api_id_type}({self.get_api_id_values(api_id_type)})"
                statement += END_OF_STATEMENT_CONSTANT
            elif self.is_long_click_event():
                api_id_type = self.get_api_id_type()
                statement += f"{TAB_CONSTANT}onEventLongClickingBy{api_id_type}({self.get_api_id_values(api_id_type)})"
                statement += END_OF_STATEMENT_CONSTANT
            elif self.is_back_event():
                statement += f"{TAB_CONSTANT}onEventGlobalBack()"
                statement += END_OF_STATEMENT_CONSTANT
            elif self.is_ime_enter_event():
                statement += f"{TAB_CONSTANT}onEventImeEnter()"
                statement += END_OF_STATEMENT_CONSTANT
            else:
                raise MethodException("The action control is not supported: ")
        # 2. the statement is a mutable event with parameter
        else:
            # event is an input, no condition, but parameterize the input value
            if self.is_input_event():
                api_id_type = self.get_api_id_type()
                statement += (f"{TAB_CONSTANT}onEventInputBy{api_id_type}({self.get_api_id_values(api_id_type)}, "
                              f"{self.get_parameter_name()})")
                statement += END_OF_STATEMENT_CONSTANT
            # event is a click, add condition
            elif self.is_click_event():
                api_id_type = self.get_api_id_type()
                statement += (f"{TAB_CONSTANT}if ({self.get_parameter_name()}.toLowerCase().equals("
                              f"\"{self.get_parameter_instance().lower()}\"))\n")
                statement += (f"{TAB_CONSTANT}{TAB_CONSTANT}onEventClickingBy{api_id_type}("
                              f"{self.get_api_id_values(api_id_type)})")
                statement += END_OF_STATEMENT_CONSTANT
            elif self.is_long_click_event():
                api_id_type = self.get_api_id_type()
                statement += (f"{TAB_CONSTANT}if ({self.get_parameter_name()}.toLowerCase().equals("
                              f"\"{self.get_parameter_instance().lower()}\"))\n")
                statement += (f"{TAB_CONSTANT}{TAB_CONSTANT}onEventLongClickingBy{api_id_type}("
                              f"{self.get_api_id_values(api_id_type)})")
                statement += END_OF_STATEMENT_CONSTANT
            elif self.is_back_event():
                statement += f"{TAB_CONSTANT}onEventGlobalBack()"
                statement += END_OF_STATEMENT_CONSTANT
            elif self.is_ime_enter_event():
                statement += f"{TAB_CONSTANT}onEventImeEnter()"
                statement += END_OF_STATEMENT_CONSTANT
            else:
                raise MethodException("The action control is not supported: ")
            pass

        return statement

    def get_input_value(self):
        action = self._event.get_gui_control()
        value = action.get_control_feature('value')
        return f'\"{value}\"'

    def get_api_id_type(self):
        """
        This method is used to get the id type of the element used in API calls.
        - text -> 'Text'
        - content-desc -> 'CD'
        - resource-id -> 'ResourceId'

        for example, onEventInputBy(CD) or onEventInputBy(Text) or onEventInputBy(ResourceId)

        :return: return CD or Text or ResourceId string
        """
        identifier = self._event.get_gui_element().get_prior_id()
        text, content_desc, resource_id = self._identifiers_value_tuple

        if identifier == 'text':
            if text is not None and text != "":
                return 'Text'
            raise MethodException("API id type failed since element prior id is empty")

        elif identifier == 'content-desc':
            if content_desc is not None and content_desc != "":
                return 'CD'
            raise MethodException("API id type failed since element prior id is empty")

        elif identifier == 'resource-id':
            if resource_id is not None and resource_id != "":
                return 'ResourceId'
            raise MethodException("API id type failed since element prior id is empty")

        else:
            raise MethodException("Identifiers are not any of the (text, content_desc, resource_id) :" + identifier)

    def get_api_id_values(self, api_id_type):
        """
        This method is used to get the all non-empty id values as a list of arguments during API invocation
        For example,
            - "OK", "android:id/button1"
            - "Create new label"
        :return:
        """
        text, content_desc, resource_id = self._identifiers_value_tuple

        if api_id_type == 'Text':  # the element has text
            if resource_id is not None and resource_id != "":  # element has optional resource_id
                return f"\"{text}\", \"{resource_id}\""
            else:
                return f"\"{text}\""
        elif api_id_type == 'CD':  # the element has content_desc
            if resource_id is not None and resource_id != "":  # element has optional resource_id
                return f"\"{content_desc}\", \"{resource_id}\""
            else:
                return f"\"{content_desc}\""
        elif api_id_type == 'ResourceId':  # the element has resource_id
            return f"\"{resource_id}\""
        else:
            raise MethodException("API id type is not supported: " + api_id_type)

    def get_parameter_instance(self):
        name, identifier, instance = self._parameter
        return instance

    def get_parameter_identifier(self) -> str:
        name, identifier, instance = self._parameter
        return identifier

    def get_parameter_name(self) -> str:
        name, identifier, instance = self._parameter
        return name




class Header:
    """
    Header class includes two attributes:
    - name: method's name
    - parameters name set,
      For example, "param1", "param2"
    """

    def __init__(self, statement_queue: Queue, method: GUIMethod):
        """
        Constructor of Header obj based on statement_queue and method
        :param statement_queue: queue of all statements in method
        :param method: GUImethod obj
        """

        self._name = ''
        self._parameters_name_set = set()

        # assign the name
        name = method.get_name()
        if name is not None and name != '':
            self._name = name
        else:
            raise MethodException("The method name is empty or None")

        # assign the parameters
        self._collect_parameters_name_set(statement_queue)

    def get_name(self):
        return self._name

    def _collect_parameters_name_set(self, statement_queue: Queue):
        """
        Collect all the parameter names to a set. Ignore the duplicated names.
        For example, param1, param2, ...
        :param statement_queue:
        :return:
        """
        if not statement_queue.empty():
            # iterate the queue to retrieve all parameter names
            for statement in list(statement_queue.queue):
                param_name: str = statement.get_parameter_name()

                # add non-empty parameter names to set
                if param_name is not None and param_name != "":
                    self._parameters_name_set.add(param_name)

    def to_code(self, language: str) -> str:
        """
        Write the header to code in specified language
        For example, "public void method_name (parameter list ...)"
        :param language:
        :return:
        """

        if language.lower() != 'java':
            raise MethodException("target language is not supported when generating statement in code: " +
                                  language)

        header = ''
        header += f'public void {self._name} ('  # write the modifiers of method header

        # header has parameters:
        if self._parameters_name_set:
            param_total_number = len(self._parameters_name_set)
            param_count = 0
            for parameter in self._parameters_name_set:

                header += f'String {parameter}'
                param_count += 1

                if param_count < param_total_number:  # write a comma for the next parameter
                    header += ', '
        else:
            pass

        header += ')'

        return header

    def set_name(self, new_name):
        self._name = new_name
