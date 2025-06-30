import sys

if sys.platform == 'win32':
    from msvcrt import getch
else:
    import termios
    import tty

    def getch():
        fileDescriptor = sys.stdin.fileno()
        oldSettings = termios.tcgetattr(fileDescriptor)

        try:
            tty.setraw(sys.stdin.fileno())
            character = sys.stdin.read(1).encode()
        finally:
            termios.tcsetattr(fileDescriptor, termios.TCSADRAIN, oldSettings)

        return character

__all__ = [
    'BF_DEFAULT_CELL',
    'BFInterpreter',
    'BFTokens',
    'BFExec'
]

BF_DEFAULT_CELL = 30000

def BFTokens(source):
    if not isinstance(source, str):
        raise TypeError("bf_tokens() source must be string")

    comment = False
    tokens = []

    for position, character in enumerate(source):

        if not comment and character == '#':
            comment = True
        elif comment and character == '\n':
            comment = False

        if not comment and character in '<>+-.,[]':
            tokens.append((position, character))

    return tokens

class BFInterpreter:

    def __init__(self, source, *, cell=None, input=None, output=None):
        if cell is None:
            cell = BF_DEFAULT_CELL

        if input is None:
            def input():
                while True:
                    result = ord(getch())
                    if 0 <= result <= 255:
                        return result

        if output is None:
            def output(byte):
                sys.stdout.write(chr(byte))
                sys.stdout.flush()

        if not isinstance(cell, int) or cell <= 0:
            raise TypeError("BFInterpreter() cell must be integer and greater than 0")
        if not callable(input):
            raise TypeError("BFInterpreter() input must be callable")
        if not callable(output):
            raise TypeError("BFInterpreter() output must be callable")

        self.tokens = BFTokens(source)
        self.cell = cell
        self.input = input
        self.output = output

        self.begin = False
        self.bracketMap = {}

        stack = []

        for i, (_, character) in enumerate(self.tokens):

            if character == '[':
                stack.append(i)

            elif character == ']':
                if not stack:
                    raise SyntaxError("unbalanced brackets")

                startIndex = stack.pop()

                self.bracketMap[startIndex] = i
                self.bracketMap[i] = startIndex

        if stack:
            raise SyntaxError("unbalanced brackets")

    def start(self):
        if self.begin:
            return

        self.memory = [0] * self.cell
        self.index = -1
        self.pointer = 0
        self.begin = True

    def step(self):
        if not self.begin:
            return

        self.index += 1

        while self.index < len(self.tokens):
            position, character = self.tokens[self.index]

            if character == '>':
                self.pointer += 1
                if self.pointer >= self.cell:
                    raise IndexError("pointer out of bounds")

            elif character == '<':
                self.pointer -= 1
                if self.pointer < 0:
                    raise IndexError("pointer out of bounds")

            elif character == '+':
                self.memory[self.pointer] = (self.memory[self.pointer] + 1) % 256

            elif character == '-':
                self.memory[self.pointer] = (self.memory[self.pointer] - 1) % 256

            elif character == ',':
                input = self.input()

                if not (isinstance(input, int) and 0 <= input <= 255):
                    raise TypeError("BFInterpreter() input must be returns unsigned 8-bit integer")

                self.memory[self.pointer] = input

            elif character == '.':
                self.output(self.memory[self.pointer])

            elif character == '[':
                if self.memory[self.pointer] == 0:
                    self.index = self.bracketMap[self.index]

            elif character == ']':
                if self.memory[self.pointer] != 0:
                    self.index = self.bracketMap[self.index]

            break

        else:
            self.begin = False
            return

        return self.index, self.pointer, position, character

    def stop(self):
        self.begin = False

    def __iter__(self):
        self.start()
        return self

    def __next__(self):
        result = self.step()

        if result is None:
            raise StopIteration

        return result

def BFExec(source, **kwargs):
    for _ in BFInterpreter(source, **kwargs):
        pass