from ..structs.EspressoCorrelations import EspressoCorrelations
from ..structs.UiAutomator1Actions import UiAutomator1Actions
from ..structs.UiAutomator1Criteria import UiAutomator1Criteria
from ..structs.UiAutomator2Actions import UiAutomator2Actions
from ..structs.UiAutomator2Criteria import UiAutomator2Criteria
from ..structs.EspressoActions import EspressoActions
from ..structs.EspressoCriteria import EspressoCriteria

ActionMap = {
    "UiAutomator1": UiAutomator1Actions,
    "UiAutomator2": UiAutomator2Actions,
    "Espresso": EspressoActions
}

AssertionCorrelationMap = {
    "Espresso": EspressoCorrelations
}

TextActionMap = ["replaceText", "setText", "typeText"]

WebElementMap = {
    "UiAutomator1": UiAutomator1Criteria,
    "UiAutomator2": UiAutomator2Criteria,
    "Espresso": EspressoCriteria
}
