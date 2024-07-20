import xml.etree.ElementTree as Et

from collections import deque
from typing import Callable, List, Optional


class XMLElement(Et.Element):
    INDEX_COUNTER = 1

    def __init__(self, tag: str, attrib: dict = {}, **extra):
        super().__init__(tag, attrib, **extra)
        self._parent: Optional["XMLElement"] = None
        self._depth: int = 0
        self._index: int = 0
        self._text: Optional[str] = None

    def get_parent(self) -> Optional["XMLElement"]:
        return self._parent

    def get_siblings(self) -> List["XMLElement"]:
        if self._parent is not None:
            return [elem for elem in self._parent.get_children() if elem != self]
        return []

    def get_children(self) -> List["XMLElement"]:
        return list(self)

    def append(self, element: "XMLElement"):
        super().append(element)
        element._parent = self
        element._depth = self._depth + 1
        element.set_index(XMLElement.INDEX_COUNTER)
        XMLElement.INDEX_COUNTER += 1

    def remove(self, element: "XMLElement"):
        super().remove(element)
        element._parent = None
        element._depth = 0

    def depth(self) -> int:
        return self._depth

    def find_first_child(self, callback: Callable[["XMLElement"], bool]) -> Optional["XMLElement"]:
        for child in self:
            if callback(child):
                return child
        return None

    def find_first_descendant(self, callback: Callable[["XMLElement"], bool]) -> Optional["XMLElement"]:
        for child in self:
            if callback(child):
                return child
            descendant_result = child.find_first_descendant(callback)
            if descendant_result is not None:
                return descendant_result
        return None

    def find_children(self, callback: Callable[["XMLElement"], bool]) -> List["XMLElement"]:
        return [child for child in list(self) if callback(child)]

    def find_descendants(self, callback: Callable[["XMLElement"], bool]) -> List["XMLElement"]:
        descendants: List[XMLElement] = []
        queue = deque([self])

        while queue:
            element = queue.popleft()

            if callback(element):
                descendants.append(element)

            queue.extend(element.get_children())

        return descendants

    def find_first_parent(self, callback: Callable[["XMLElement"], bool]) -> Optional["XMLElement"]:
        parent = self.get_parent()
        while parent is not None:
            if callback(parent):
                return parent
            parent = parent.get_parent()
        return None

    def find_first_ancestor(self, callback: Callable[["XMLElement"], bool]) -> Optional["XMLElement"]:
        ancestor = self.find_first_parent(callback)
        if ancestor is None:
            ancestor = self.find_parents(callback)
        return ancestor

    def find_parents(self, callback: Callable[["XMLElement"], bool]) -> List["XMLElement"]:
        parents: List[XMLElement] = []
        parent = self.get_parent()
        while parent is not None:
            if callback(parent):
                parents.append(parent)
            parent = parent.get_parent()
        return parents

    def find_ancestors(self, callback: Callable[["XMLElement"], bool]) -> List["XMLElement"]:
        ancestors: List[XMLElement] = []
        parent = self.get_parent()
        while parent is not None:
            if callback(parent):
                ancestors.append(parent)
            parent = parent.get_parent()
        return ancestors

    def is_a_descendant_of(self, callback: Callable[["XMLElement"], bool]) -> bool:
        parent = self.get_parent()
        while parent is not None:
            if callback(parent):
                return True
            parent = parent.get_parent()
        return False

    def is_a_child_of(self, callback: Callable[["XMLElement"], bool]) -> bool:
        parent = self.get_parent()
        if parent is not None and callback(parent):
            return True
        return False

    def set_index(self, index: int):
        self._index = index

    def index(self, **kwargs) -> int:
        return self._index

    def as_uis1(self) -> "UiSelector1ExprElement":
        from test2va.parser.structs.UiAutomator1ExprElement import UiAutomator1ExprElement as UIA1E
        u_expr = UIA1E(self.tag, self.attrib)
        u_expr.tag = self.tag
        u_expr.attrib = self.attrib
        u_expr._text = self._text
        u_expr._parent = self._parent
        u_expr._depth = self._depth
        u_expr._index = self._index
        u_expr._element = self
        return u_expr

    def as_uia2(self) -> "UiAutomator2ExprElement":
        from test2va.parser.structs.UiAutomator2ExprElement import UiAutomator2ExprElement as UIA2E
        u2_expr = UIA2E(self)
        u2_expr.tag = self.tag
        u2_expr.attrib = self.attrib
        u2_expr.text = self.text
        u2_expr._parent = self._parent
        u2_expr._depth = self._depth
        u2_expr._index = self._index
        u2_expr._element = self
        return u2_expr

    def as_espresso_decl(self) -> "EspressoDeclElement":
        from test2va.parser.structs.EspressoDeclElement import EspressoDeclElement as EDE
        e_decl = EDE(self)
        e_decl.tag = self.tag
        e_decl.attrib = self.attrib
        e_decl.text = self.text
        e_decl._parent = self._parent
        e_decl._depth = self._depth
        e_decl._index = self._index
        e_decl._element = self
        return e_decl

    @property
    def text(self):
        return self._text or ""

    @text.setter
    def text(self, value: str):
        self._text = value

    def _extend_element(self, element: "XMLElement"):
        # Copy attributes from the original element
        self.tag = element.tag
        self.attrib = element.attrib

        # Copy the text content
        self._text = element.text

    def __getattr__(self, attr: str):
        # Forward attribute access to the underlying Element object
        return getattr(super(), attr)

    def __repr__(self):
        return f"XMLElement(tag='{self.tag}')"
