def load(reg, memreg):
    pass


def store(memreg, reg):
    pass


def mov_low1(reg, imm):
	reg._state = b"00000000" + imm


def mov_low2(reg, imm):
	reg._state = b"00000000" + imm


def mov_high1(reg, imm):
    reg._state = imm + reg[8:]


def mov_high2(reg, imm):
    reg._state = imm + reg[8:]


def mov(reg1, reg2):
    reg1._state = reg2._state


def push(reg):
    pass


def pop(reg):
    pass


def add(reg1, reg2, reg3):
    reg1._state = reg2._state + reg3._state


# def


fucnctions_dictionary = {"load":load(), "mov_low1":mov_low1(),
                        "mov_low2":mov_low2(), "mov_high1":mov_high1(),
                        "mov_high2":mov_high2(), "mov":mov(), }
