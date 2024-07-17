import re


def is_float(op):
    return bool(re.fullmatch("[-+]?\d*\.*\d+", op))


def is_number(op):
    return bool(re.fullmatch("[-+]?\d+", op))


def type_fallback(arg, unknown_type_value=0):
    if type(arg) == float:
        return arg
    elif type(arg) == int:
        return arg
    elif type(arg) == str:
        if is_float(arg):
            return float(arg)
        elif is_number(arg):
            return int(arg)
        else:
            return unknown_type_value
    else:
        return unknown_type_value
