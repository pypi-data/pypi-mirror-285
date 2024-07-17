import sys
from .type_fallback import type_fallback


def subtract(*ops):
    total = 0
    for op in ops:
        if type(op) == list or type(op) == tuple or type(op) == set:
            for o in op:
                num = type_fallback(o)
                if op.index(o) == 0:
                    total = num
                else:
                    total = total - num
        else:
            num = type_fallback(op)
            if ops.index(op) == 0:
                total = num
            else:
                total = total - num
    return total
