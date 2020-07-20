from bitarray import bitarray


class Shell:
    """
    Class for shell representation
    """
    def __init__(self, io_type, start=0, end=0):
        """
        Create new shell

        :param io_type: I/O type (MMIO, special commands)
        :return: NoneType
        """
        self.start_point = start
        self.end_point = end
        self.io_type = io_type
        self._state = bitarray("0"*160)

    def in_shell(self):
        # TODO: implement input
        pass

    def out_shell(self, value):
        """
        Write value into the shell (to the right)

        :param value: value to be written
        """
        self._state += value
        self._state = self._state[-160:]

    def __str__(self):
        """
        Return string representation of the shell

        :return: ascii-decoded slots of the shell
        """
        return self._state.tobytes().decode("ascii")



