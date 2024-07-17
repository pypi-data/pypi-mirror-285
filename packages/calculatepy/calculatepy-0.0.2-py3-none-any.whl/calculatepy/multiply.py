from helpers.operand_type import check_operand_type
def multiply(*ops):
    total = 0
    for op in ops:
        if type(op) == list or type(op) == tuple or type(op) == set:
            for o in op:
                num = check_operand_type(o, 1)
                if op.index(o) == 0:
                    total = num
                else:
                    total = total * num
        else:
            num = check_operand_type(op, 1)
            if ops.index(op) == 0:
                total = num
            else:
                total = total * num
    return total
