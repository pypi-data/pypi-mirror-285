from test2va.generator.exceptions.GUIException import GUIException

TEXT_FEATURE_CONSTANT_STRING: str = 'text'
CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING: str = 'content-desc'
RESOURCE_ID_FEATURE_CONSTANT_STRING: str = 'resource-id'
CLASS_FEATURE_CONSTANT_STRING: str = 'class'
DISPLAYED_FEATURE_CONSTANT_STRING: str = 'displayed'

class GUIElement:
    # constructor
    def __init__(self, criteria_list: list = None):
        """
        This constructor is used to hold all the information of an GUI element.
        Including:
        - all features: ['text', 'content-desc', 'resource-id', 'class', 'displayed']
        - _prior_id: the identifier flag used when invoke test2va API

        :param criteria_list:
        """
        # features of an UI element include: name, type, content
        self._features = {
            TEXT_FEATURE_CONSTANT_STRING: '',
            CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING: '',
            RESOURCE_ID_FEATURE_CONSTANT_STRING: '',
            CLASS_FEATURE_CONSTANT_STRING: '',
            DISPLAYED_FEATURE_CONSTANT_STRING: ''
        }
        self._prior_id = ''

        if criteria_list is None:
            return

        for criteria in criteria_list:
            if not criteria['nested']:
                # handle content description feature, the value usually will be string
                if criteria['name'] == 'withContentDescription':
                    # get value
                    value = ""
                    if criteria['args'][0]['type'] == 'string':
                        value = criteria['args'][0]['content']
                    else:
                        print("error happens")
                    # assign value to key 'content-desc'
                    self._features[CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING] = value

                # handle isDisplay feature, the default value is true
                elif criteria['name'] == 'isDisplayed':
                    value = True
                    # assign value to key 'displayed'
                    self._features[DISPLAYED_FEATURE_CONSTANT_STRING] = True

                # handle content Text, the value usually will be string
                elif criteria['name'] == 'withText':
                    # get value
                    value = ""
                    if criteria['args'][0]['type'] == 'string':
                        value = criteria['args'][0]['content']
                    else:
                        print("error happens")
                    # assign value to key 'text'
                    self._features[TEXT_FEATURE_CONSTANT_STRING] = value

                # handle content resource id, the value usually will be string
                elif criteria['name'] == 'withId':
                    # get value
                    value = ""
                    if criteria['args'][0]['type'] == 'string':
                        value = criteria['args'][0]['content']
                    else:
                        print("error happens")
                    # assign value to key 'resource-id'
                    self._features[RESOURCE_ID_FEATURE_CONSTANT_STRING] = value

                else:
                    print("unsupported feature: " + str(criteria['name']))

    def set_feature(self, feature_name: str, feature_value):

        # do not set value to None
        if feature_value is None:
            return

        if feature_name in [TEXT_FEATURE_CONSTANT_STRING, CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING,
                            RESOURCE_ID_FEATURE_CONSTANT_STRING, CLASS_FEATURE_CONSTANT_STRING,
                            DISPLAYED_FEATURE_CONSTANT_STRING]:
            self._features[feature_name] = feature_value
        else:
            raise GUIException("feature name is not pre-defined: " + feature_name)

    def get_feature_by_name(self, feature_name):
        if feature_name in [TEXT_FEATURE_CONSTANT_STRING, CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING,
                            RESOURCE_ID_FEATURE_CONSTANT_STRING, CLASS_FEATURE_CONSTANT_STRING,
                            DISPLAYED_FEATURE_CONSTANT_STRING]:
            return self._features[feature_name]
        else:
            raise GUIException("feature name is not pre-defined: " + feature_name)

    def get_all_features(self):
        return self._features

    def get_identifiers(self) -> tuple:
        """
        Return the three identifiers of element in tuple
        for example, ('text', 'content-desc', 'resource-id')
        :return:
        """
        identifier_tuple = (self._features[TEXT_FEATURE_CONSTANT_STRING],
                            self._features[CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING],
                            self._features[RESOURCE_ID_FEATURE_CONSTANT_STRING])
        return identifier_tuple

    def __str__(self):
        s = ""
        for key, value in self._features.items():
            s = s + f"key: {key} | value: {value} \n"

        return s

    def update_prior_id(self):

        if (self._features[TEXT_FEATURE_CONSTANT_STRING] is not None
                and self._features[TEXT_FEATURE_CONSTANT_STRING] != ""):
            self._prior_id = TEXT_FEATURE_CONSTANT_STRING
        elif (self._features[CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING] is not None
              and self._features[CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING] != ""):
            self._prior_id = CONTENT_DESCRIPTION_FEATURE_CONSTANT_STRING
        elif (self._features[RESOURCE_ID_FEATURE_CONSTANT_STRING] is not None
              and self._features[RESOURCE_ID_FEATURE_CONSTANT_STRING] != ""):
            self._prior_id = RESOURCE_ID_FEATURE_CONSTANT_STRING
        else:
            self._prior_id = ''
            # raise GUIException("all identifiers (text, content_desc, resource_id) are either none or "
            #                    "empty, no prior id")
        pass

    def get_prior_id(self) -> str:
        return self._prior_id

class GUIControl:
    def __init__(self, control: dict = None, name: str = None, type: str = None, value: str = None):
        """
        Constructor of GUIControl

        :param control: parsed result json object
        :param name:  'click', 'replaceText'
        :param type:  'String'
        :param value:  'Meeting'
        """

        self._control_features: dict = {'name': '', 'type': '', 'value': ''}

        # assign from feature values directly
        if not control:
            self._control_features['name'] = name
            self._control_features['type'] = type
            self._control_features['value'] = value
        # assign from parsed result
        else:
            self._control_features['name'] = control['action']
            if not control['args']:
                if self._control_features['name'].lower() == "click".lower():
                    self._control_features['type'] = ''
                    self._control_features['value'] = ''
            else:
                self._control_features['type'] = control['args'][0]["type"]
                self._control_features['value'] = control['args'][0]["content"]

    def get_control_features(self):
        return self._control_features

    def get_control_feature(self, key: str):
        """
        features include: 'name', 'type', and 'value'
        :param key:
        :return:
        """
        if key in ['name', 'type', 'value']:
            return self._control_features[key]
        else:
            raise GUIException("Unexpected feature label:" + key)

    def get_control_feature_name(self):
        return self._control_features['name']

    def get_control_feature_type(self):
        return self._control_features['type']

    def get_control_feature_value(self):
        return self._control_features['value']

    def __str__(self):
        return (f"GUIControl name: {self._control_features['name']}; "
                f"type: {self._control_features['type']}; "
                f"value: {self._control_features['value']} ")


class GUIEvent:
    # constructor
    def __init__(self, event: dict, control: GUIControl = None, element: GUIElement = None):
        """
        The constructor has two ways to build an guiEvent obj
        1) throw event dict to build GUIControl and GUIElement separately
        2) directly assign the built GUIControl and GUIElement to GUIEvent

        :param control: GUIControl object
        :param element: GUIElement object
        :param event: json dictionary parsed from basic test
        """
        if event:
            self._control: GUIControl = self._build_control(event["action"])
            self._element: GUIElement = self._build_gui_element(event["criteria"])
        else:
            self._control: GUIControl = control
            self._element: GUIElement = element

    def _build_control(self, action):
        return GUIControl(action)

    def _build_gui_element(self, criteria_list):
        obj = GUIElement(criteria_list)
        return obj

    def get_gui_element(self):
        return self._element

    def set_gui_element(self, element: GUIElement):
        self._element = element

    def get_gui_control(self):
        return self._control

    def set_gui_control(self, control: GUIControl):
        self._control = control

    def __str__(self):
        return f"GUIEvent \n control: {self._control} \n element: {self._element}"


class GUIMethod:
    # constructor
    def __init__(self, json_data: list):
        self._name = ""
        self._parameter = {}
        self._gui_events = []

        self.set_name(json_data[0]["name"])
        self.set_events(json_data[0]["selectors"])

    # define name
    def set_name(self, new_name):
        if new_name and new_name.strip():
            self._name = new_name
        else:
            print("Method name does not exist!!")

    def set_events(self, event_list):
        for event in event_list:
            e: GUIEvent = GUIEvent(event)
            self._gui_events.append(e)

    def set_event_by_index(self, new_event: GUIEvent, index: int):
        if 0 <= index < len(self._gui_events):
            self._gui_events[index] = new_event
        else:
            raise GUIException(f"set event to an invalid index: {index}")

    def set_para(self, para: dict):
        self._parameter = para

    def get_name(self):
        return self._name

    def get_para(self):
        return self._parameter

    def get_events(self):
        return self._gui_events

    def get_event_by_index(self, index: int) -> GUIEvent:
        return self._gui_events[index]

    def __str__(self):
        return f"GUIMethod \nname: {self._name} \nargs: {self._parameter} \nevents: {self._gui_events} "
