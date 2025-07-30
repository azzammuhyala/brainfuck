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
    'BFInterpreter',
    'BFExec'
]

class BFInterpreter:

    def __init__(self, source, *, cells=None, input=None, output=None):
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

        if not isinstance(source, str):
            raise TypeError("BFInterpreter() source must be string")
        if not isinstance(cells, (int, type(None))):
            raise TypeError("BFInterpreter() cells must be integer")
        if not callable(input):
            raise TypeError("BFInterpreter() input must be callable")
        if not callable(output):
            raise TypeError("BFInterpreter() output must be callable")

        if cells is not None and cells <= 0:
            raise ValueError("BFInterpreter() cells must be greater than 0")

        self.running = False

        self.source = source
        self.cells = cells
        self.input = input
        self.output = output

        self._tokenIndex = -1
        self._tokens = []
        self._bracketMap = {}

        stack = []
        comment = False
        tokenIndex = 0

        for position, character in enumerate(source):

            if not comment and character == '#':
                comment = True
            elif comment and character == '\n':
                comment = False

            if not comment and character in '<>+-.,[]':

                if character == '[':
                    stack.append(tokenIndex)

                elif character == ']':
                    if not stack:
                        raise SyntaxError("unbalanced brackets")

                    startIndex = stack.pop()

                    self._bracketMap[startIndex] = tokenIndex
                    self._bracketMap[tokenIndex] = startIndex

                self._tokens.append((position, character))
                tokenIndex += 1

        if stack:
            raise SyntaxError("unbalanced brackets")

    def start(self):
        if self.running:
            return

        self._tokenIndex = -1

        self.running = True
        self.memory = [0]
        self.point = 0

        if self.cells is not None:
            self.memory *= self.cells

    def step(self):
        if not self.running:
            return

        self._tokenIndex += 1

        if self._tokenIndex >= len(self._tokens):
            self.running = False
            return

        position, character = self._tokens[self._tokenIndex]
        dataPointer = self.memory[self.point]

        if character == '>':
            self.point += 1
            if self.cells is None:
                if self.point == len(self.memory):
                    self.memory.append(0)
            elif self.point >= self.cells:
                raise IndexError("pointer out of bounds")

        elif character == '<':
            if self.point == 0:
                raise IndexError("pointer out of bounds")
            self.point -= 1

        elif character == '+':
            self.memory[self.point] = (dataPointer + 1) % 256

        elif character == '-':
            self.memory[self.point] = (dataPointer - 1) % 256

        elif character == ',':
            input = self.input()

            if not (isinstance(input, int) and 0 <= input <= 255):
                raise TypeError("BFInterpreter() input must be returns unsigned 8-bit integer")

            self.memory[self.point] = input

        elif character == '.':
            self.output(dataPointer)

        elif character == '[' and dataPointer == 0:
            self._tokenIndex = self._bracketMap[self._tokenIndex]

        elif character == ']' and dataPointer != 0:
            self._tokenIndex = self._bracketMap[self._tokenIndex]

        return self.point, position, character

    def stop(self, cleanUp=True):
        if not self.running:
            return

        self.running = False

        if cleanUp:
            del self.memory, self.point

    def __iter__(self):
        self.start()

        return self

    def __next__(self):
        result = self.step()

        if result is None:
            raise StopIteration

        return result

def BFExec(source, **kwargs):
    interpreter = BFInterpreter(source, **kwargs)

    for _ in interpreter:
        pass

    interpreter.stop()