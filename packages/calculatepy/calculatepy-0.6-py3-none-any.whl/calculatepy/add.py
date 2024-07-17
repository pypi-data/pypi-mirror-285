from utils import check_operand_type


def add(*ops):
    total = 0
    for op in ops:
        if type(op) == list or type(op) == tuple or type(op) == set:
            for o in op:
                num = check_operand_type(o)
                total = total + num
        else:
            num = check_operand_type(op)
            total = total + num
    return total
