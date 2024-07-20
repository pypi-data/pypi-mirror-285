from typing import List, TypedDict, Literal


class CriteriaArgument(TypedDict):
    type: str
    content: str


class CriteriaData(TypedDict):
    name: str
    args: List[CriteriaArgument]
    nested: bool


class ActionArg(TypedDict):
    type: str
    content: str
    nested: bool


class NestedActionArg(TypedDict):
    type: str
    criteria: List[CriteriaData]
    nested: bool


class ActionData(TypedDict):
    action: str
    args: List[ActionArg | NestedActionArg]


class NestedCriteria(TypedDict):
    name: str
    args: List[CriteriaData]
    nested: bool


class SelectorData(TypedDict):
    type: Literal["UiAutomator1", "UiAutomator2", "Espresso"]
    criteria: List[CriteriaData | NestedCriteria] | None
    action: ActionData | NestedActionArg
    string: str | None
    search_type: Literal["allOf", "anyOf", "is", "not", "endsWith", "startsWith", "instanceOf"] | None


class AssertionData(TypedDict):
    method: Literal["assertEquals", "assertNotEquals", "assertTrue", "assertFalse", "assertSame", "assertNotSame",
    "assertNull", "assertNotNull", "assertThrows"] | None
    selector: SelectorData


class ParsedData(TypedDict):
    name: str
    selectors: List[SelectorData]
    before: List[SelectorData] | None
    assertion: List[AssertionData]
    library: Literal["UiAutomator1", "UiAutomator2", "Espresso"]
