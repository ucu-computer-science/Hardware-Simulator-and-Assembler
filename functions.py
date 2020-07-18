def load(*operands):
    pass


def store(*operands):
    pass


def mov_low1(*operands):
	operands[0]._state = b"00000000" + operands[1]


def mov_low2(*operands):
	operands[0]._state = b"00000000" + operands[1]


def mov_high1(*operands):
    operands[0]._state = operands[1] + operands[0][8:]


def mov_high2(*operands):
    operands[0]._state = operands[1] + operands[0][8:]


def mov(*operands):
    operands[0]._state = operands[1]._state


def push(reg):
    pass


def pop(reg):
    pass


def add(reg1, reg2, reg3):
    reg1._state = reg2._state + reg3._state


def sub(reg1, reg2, reg3):
    reg1._state = reg2._state - reg3._state


def mul(reg1, reg2, reg3):
    reg1._state = reg2._state * reg3._state


def div(reg1, reg2, reg3):
    reg1._state = reg2._state / reg3._state



fucnctions_dictionary = {"load":load, "mov_low1":mov_low1,
                        "mov_low2":mov_low2, "mov_high1":mov_high1,
                        "mov_high2":mov_high2, "mov":mov, }
