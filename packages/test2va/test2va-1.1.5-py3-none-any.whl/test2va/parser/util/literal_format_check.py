from ...parser.types.LibTypes import ActionArg


def literal_format_check(literal_data: ActionArg | dict):
    if literal_data["type"] == "string":
        literal_data["content"] = literal_data["content"][1:-1]
    elif literal_data["type"] == "number":
        res = parse_literal_num(literal_data["content"])
        literal_data["type"] = res[0]
        literal_data["content"] = res[1]


def parse_literal_num(num_str):
    try:
        # Handling hexadecimal, binary, and octal
        if num_str.startswith("0x") or num_str.startswith("0X"):  # Hexadecimal
            value = int(num_str, 16)
            return "number", str(value)
        elif num_str.startswith("0b") or num_str.startswith("0B"):  # Binary
            value = int(num_str, 2)
            return "number", str(value)
        elif num_str.startswith("0") and len(num_str) > 1:  # Octal
            value = int(num_str, 8)
            return "number", str(value)

        # Handling float, double and long
        if num_str.endswith(("f", "F")):  # Float
            return "float", str(float(num_str[:-1]))
        elif num_str.endswith(("d", "D")) or "." in num_str:  # Double
            return "float", str(float(num_str.rstrip("dD")))
        elif num_str.endswith(("l", "L")):  # Long
            return "number", str(int(num_str[:-1]))

        # Default case - Integer
        return "number", str(int(num_str))
    except ValueError:
        raise ValueError(f"Invalid Java number format: {num_str}")
