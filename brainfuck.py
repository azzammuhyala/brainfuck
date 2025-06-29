"""
BrainFuck Interpreter
=====================
Module to parse and run brainfuck code, all written in python code!
"""

import sys
import numpy
import getch
import typing

__all__: typing.List[str] = [
    'BF_DEFAULT_CELL',

    'BFInterpreter',

    'bf_tokens',
    'bf_exec'
]

BF_DEFAULT_CELL: int = 30000

def bf_tokens(source: str) -> typing.List[typing.Tuple[int, typing.Literal['<', '>', '+', '-', '.', ',', '[', ']']]]:

    """
    Converts brainfuck source code to token chunks.
    Supports "#" comment feature and ignores invalid characters.
    """

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

    """ BrainFuck Interpreter """

    def __init__(
        self,
        source: str,
        *,
        cell: typing.Optional[int] = None,
        input: typing.Optional[typing.Callable[[], int]] = None,
        output: typing.Optional[typing.Callable[[int], None]] = None
    ) -> None:

        """
        Initializes the BrainFuck Interpreter.

        param:
            source: BrainFuck source code.
            cell: Initial cell value. Defaults to BF_DEFAULT_CELL.
            input: Input function. Defaults to None (uses getch).
            output: Output function. Defaults to None (uses sys.stdout).
        """

        if cell is None:
            cell = BF_DEFAULT_CELL

        if input is None:
            def input():
                return ord(getch.getch())

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
                    self.tokens = []
                    self.bracket_map = {}
                    raise SyntaxError("unmatched ']'")

                start_index = stack.pop()

                self.bracket_map[start_index] = i
                self.bracket_map[i] = start_index

        if stack:
            self.tokens = []
            self.bracket_map = {}
            raise SyntaxError("unmatched '['")

    def __iter__(self) -> typing.Self:

        """
        Start code execution.
        """

        if not self.begin:
            self.array = numpy.zeros((self.cell,), dtype=numpy.uint8)
            self.index = -1
            self.pointer = 0
            self.begin = True

        return self

    def __next__(self) -> typing.Tuple[int, int, int, typing.Literal['<', '>', '+', '-', '.', ',', '[', ']']]:

        """
        Execution of the code.

        returns:
            a tuple contains the values (token index, pointer, character position, character)
        """

        if not self.begin:
            raise StopIteration

        self.index += 1

        while self.index < len(self.tokens):
            pos, char = self.tokens[self.index]

            if char == '>':
                self.pointer += 1
                if self.pointer >= self.cell:
                    raise IndexError("pointer out of range")

            elif char == '<':
                self.pointer -= 1
                if self.pointer < 0:
                    raise IndexError("pointer out of range")

            elif char == '+':
                self.array[self.pointer] = (int(self.array[self.pointer]) + 1) % 256

            elif char == '-':
                self.array[self.pointer] = (int(self.array[self.pointer]) - 1) % 256

            elif char == ',':
                inp = self.input()

                if not (isinstance(inp, int) and 0 <= inp <= 255):
                    raise TypeError("BFInterpreter() input must be returns unsigned 8-bit integer")

                self.array[self.pointer] = inp

            elif char == '.':
                self.output(int(self.array[self.pointer]))

            elif char == '[':
                if self.array[self.pointer] == 0:
                    self.index = self.bracket_map[self.index]

            elif char == ']':
                if self.array[self.pointer] != 0:
                    self.index = self.bracket_map[self.index]

            break

        else:
            self.begin = False
            raise StopIteration

        return self.index, self.pointer, pos, char

def bf_exec(source: str, **kwargs) -> None:

    """
    Execute BrainFuck code from a string.
    """

    for _ in BFInterpreter(source, **kwargs):
        pass