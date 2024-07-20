import re


def camel_to_snake(text):
    if text.lower() == "is":
        return "_is"
    return re.sub('([A-Z])', r'_\1', text).lower()