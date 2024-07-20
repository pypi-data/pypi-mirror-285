def build_xpath_from_element(element):
    xpath_parts = []

    for attr, value in element.attrib.items():
        # Skip empty attributes or attributes with special characters
        if not value or " " in value or attr == "checked" or attr == "selected":
            continue

        xpath_parts.append(f"@{attr}='{value}'")

    xpath = "//" + element.tag + "[" + " and ".join(xpath_parts) + "]"
    return xpath
