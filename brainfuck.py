import sys

if sys.platform == 'win32':
    import msvcrt

    def getch():
        return msvcrt.getch()
else:
    import termios
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1).encode()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch

__all__ = [
    'BF_DEFAULT_CELL',
    'BFInterpreter',
    'bf_tokens',
    'bf_exec'
]

BF_DEFAULT_CELL = 30000

def bf_tokens(source):
    if not isinstance(source, str):
        raise TypeError("bf_tokens() source must be string")

    comment = False
    tokens = []

    for index, char in enumerate(source):

        if not comment and char == '#':
            comment = True
        elif comment and char == '\n':
            comment = False

        if not comment and char in '<>+-.,[]':
            tokens.append((index, char))

    return tokens

class BFInterpreter:

    def __init__(self, source, *, cell=None, input=None, output=None):
        if cell is None:
            cell = BF_DEFAULT_CELL

        if input is None:
            def input():
                return ord(getch())

        if output is None:
            def output(char):
                sys.stdout.write(chr(char))
                sys.stdout.flush()

        if not isinstance(cell, int) or cell <= 0:
            raise TypeError("BFInterpreter() cell must be integer and greather than 0")
        if not callable(input):
            raise TypeError("BFInterpreter() input must be callable")
        if not callable(output):
            raise TypeError("BFInterpreter() output must be callable")

        self.tokens = bf_tokens(source)
        self.cell = cell
        self.input = input
        self.output = output

        self.begin = False
        self.bracket_map = {}

        stack = []

        for i, (pos, char) in enumerate(self.tokens):

            if char == '[':
                stack.append(i)

            elif char == ']':
                if not stack:
                    raise SyntaxError("unbalanced brackets")

                start_index = stack.pop()

                self.bracket_map[start_index] = i
                self.bracket_map[i] = start_index

        if stack:
            raise SyntaxError("unbalanced brackets")

    def start(self):
        if not self.begin:
            self.array = [0] * self.cell
            self.index = -1
            self.pointer = 0
            self.begin = True

    def step(self):
        if not self.begin:
            return

        self.index += 1

        while self.index < len(self.tokens):
            pos, char = self.tokens[self.index]

            if char == '>':
                self.pointer += 1
                if self.pointer >= self.cell:
                    raise IndexError("pointer out of bounds")

            elif char == '<':
                self.pointer -= 1
                if self.pointer < 0:
                    raise IndexError("pointer out of bounds")

            elif char == '+':
                self.array[self.pointer] = (self.array[self.pointer] + 1) % 256

            elif char == '-':
                self.array[self.pointer] = (self.array[self.pointer] - 1) % 256

            elif char == ',':
                inp = self.input()

                if not (isinstance(inp, int) and 0 <= inp <= 255):
                    raise TypeError("BFInterpreter() input must be returns unsigned 8-bit integer")

                self.array[self.pointer] = inp

            elif char == '.':
                self.output(self.array[self.pointer])

            elif char == '[':
                if self.array[self.pointer] == 0:
                    self.index = self.bracket_map[self.index]

            elif char == ']':
                if self.array[self.pointer] != 0:
                    self.index = self.bracket_map[self.index]

            break

        else:
            self.begin = False
            return

        return self.index, self.pointer, pos, char

    def __iter__(self):
        self.start()
        return self

    def __next__(self):
        result = self.step()
        if result is None:
            raise StopIteration
        return result

def bf_exec(source, **kwargs):
    for _ in BFInterpreter(source, **kwargs):
        pass