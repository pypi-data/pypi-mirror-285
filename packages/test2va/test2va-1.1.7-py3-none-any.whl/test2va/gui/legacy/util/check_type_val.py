
# Val is always a string.
# Return true or false
def check_type_val(type, val):
    if type == "str":
        return True
    elif type == "int":
        try:
            int(val)
            return True
        except ValueError:
            return False
    elif type == "bool":
        return val.lower() == "true" or val.lower() == "false"
