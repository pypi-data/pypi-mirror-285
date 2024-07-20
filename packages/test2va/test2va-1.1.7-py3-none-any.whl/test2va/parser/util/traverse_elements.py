from collections import deque

from test2va.parser.structs.XMLElement import XMLElement


def traverse_elements(element):
    root = XMLElement(element.tag, element.attrib)
    root._parent = None
    root._depth = 0
    root._extend_element(element)

    queue = deque([(root, element)])

    while queue:
        extended_parent, xml_parent = queue.popleft()

        for child in xml_parent:
            extended_child = XMLElement(child.tag, child.attrib)
            extended_child._extend_element(child)
            extended_child._parent = extended_parent
            extended_child._depth = extended_parent._depth + 1
            extended_parent.append(extended_child)
            queue.append((extended_child, child))

    return root
