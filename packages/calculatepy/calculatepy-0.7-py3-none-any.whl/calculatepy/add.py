import sys
from .type_fallback import type_fallback


def add(*ops):
    total = 0
    for op in ops:
        if type(op) == list or type(op) == tuple or type(op) == set:
            for o in op:
                num = type_fallback(o)
                total = total + num
        else:
            num = type_fallback(op)
            total = total + num
    return total
