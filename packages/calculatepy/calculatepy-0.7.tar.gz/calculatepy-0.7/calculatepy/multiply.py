import sys
from .type_fallback import type_fallback


def multiply(*ops):
    total = 0
    for op in ops:
        if type(op) == list or type(op) == tuple or type(op) == set:
            for o in op:
                num = type_fallback(o, 1)
                if op.index(o) == 0:
                    total = num
                else:
                    total = total * num
        else:
            num = type_fallback(op, 1)
            if ops.index(op) == 0:
                total = num
            else:
                total = total * num
    return total