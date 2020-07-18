def load(operands):
    pass


def store(operands):
    pass


def mov_low1(operands):
	operands[0]._state = b"00000000" + operands[1]


def mov_low2(operands):
	operands[0]._state = b"00000000" + operands[1]


def mov_high1(operands):
    operands[0]._state = operands[1] + operands[0][8:]


def mov_high2(operands):
    operands[0]._state = operands[1] + operands[0][8:]


def mov(operands):
    operands[0]._state = operands[1]


def push(operands):
    pass


def pop(operands):
    pass


def add(operands):
    operands[0]._state = bin(int(perands[1]._state) + int(operands[2]._state))


def sub(operands):
    operands[0]._state = bin(int(operands[1]._state) - int(operands[2]._state))


def mul(operands):
    operands[0]._state = bin(int(operands[1]._state) * int(operands[2]._state))


def div(operands):
    operands[0]._state = bin(int(operands[1]._state) / int(operands[2]._state))


def and(operands):


functions_dictionary = {"load":load, "mov_low1":mov_low1,
                        "mov_low2":mov_low2, "mov_high1":mov_high1,
                        "mov_high2":mov_high2, "mov":mov,
                        "push":push, "pop":pop, "add":add,
                        "sub":sub, "mul":push, "div":div}
