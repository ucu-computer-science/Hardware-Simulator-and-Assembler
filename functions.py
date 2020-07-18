def load(operands):
    pass


def store(operands):
    pass


def mov_low1(operands):
	operands[0]._state = "00000000" + operands[1]


def mov_low2(operands):
	operands[0]._state = "00000000" + operands[1]


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
    pass


def or(operands):
    pass


def xor(operands):
    pass


def not(operands):
    pass


def lsh(operands):
    pass


def rsh(operands):
    pass


def call1(operands):
    pass


def call2(operands):
    pass


def call3(operands):
    pass


def ret(operands):
    pass


def cmp1(operands):
    pass


def cmp2(operands):
    pass


def test(operands):
    pass


functions_dictionary = {"load":load, "mov_low1":mov_low1,
                        "mov_low2":mov_low2, "mov_high1":mov_high1,
                        "mov_high2":mov_high2, "mov":mov,
                        "push":push, "pop":pop, "add":add,
                        "sub":sub, "mul":push, "div":div}
