# Original code: https://github.com/DismissedGuy/brainfuck-interpreter
# Modified to suit bot needs

class IOStream:
    def __init__(self, data=None):
        self.__buffer = data if data else ""

    def __len__(self):
        return len(self.__buffer)

    def read(self, length=None):
        if not length:
            data = self.__buffer
            self.__buffer = ""
        else:
            data = self.__buffer[:length]
            self.__buffer = self.__buffer[length:]
        return data

    def write(self, data):
        self.__buffer += data


class IncrementalByteCellArray:
    def __init__(self):
        self.__byteCells = [0]
        self.__dataPointer = 0

    def __getitem__(self, item):
        cellAmount = len(self.__byteCells)
        if item > cellAmount - 1:
            self.__extend(item - cellAmount + 1)
        return self.__byteCells[item]

    def __setitem__(self, key: int, value: int):
        cellAmount = len(self.__byteCells)
        if key > cellAmount - 1:
            self.__extend(key - cellAmount + 1)
        self.__byteCells[key] = value

    def __len__(self):
        return len(self.__byteCells)

    def __repr__(self):
        return self.__byteCells.__repr__()

    def __extend(self, size: int):
        self.__byteCells += [0] * size

    def dataPointerSet(self, decrement=False):
        if decrement:
            self.__dataPointer -= 1
        else:
            self.__dataPointer += 1

    def increment(self):
        newVal = (self.get() + 1) % 256
        self.set(newVal)

    def decrement(self):
        newVal = self.get() - 1
        if newVal < 0:
            newVal = 255
        self.set(newVal)

    def set(self, value:int):
        self.__setitem__(self.__dataPointer, value)

    def get(self):
        return self.__getitem__(self.__dataPointer)


class BrainfuckInterpreter:
    def __init__(self, commands:str):
        self.__commands = commands.replace(" ", "")
        self.__instructionPointer = 0
        self.__cells = IncrementalByteCellArray()
        self.__openingBracketIndexes = []
        self.input = IOStream()
        self.output = IOStream()

    def __lookForward(self):
        remaining = self.__commands[self.__instructionPointer:]
        count = 0
        index = self.__instructionPointer
        for command in remaining:
            if command == "[":
                count += 1
            elif command == "]":
                count -= 1
            if count == 0:
                return index
            index += 1

    def __interpret(self):
        instruction = self.__commands[self.__instructionPointer]
        if instruction == ">":
            self.__cells.dataPointerSet()
        elif instruction == "<":
            self.__cells.dataPointerSet(decrement=True)
        elif instruction == "+":
            self.__cells.increment()
        elif instruction == "-":
            self.__cells.decrement()
        elif instruction == ".":
            self.output.write(chr(self.__cells.get()))
        elif instruction == ",":
            self.__cells.set(self.input.read(1))
        elif instruction == "[":
            if self.__cells.get() == 0:
                try:
                    loopEnd = self.__lookForward()
                except ValueError:
                    raise ValueError(
                        f"No closing bracket for loop found on index: {self.__instructionPointer}"
                    )
                self.__instructionPointer = loopEnd
            else:
                self.__openingBracketIndexes.append(self.__instructionPointer)
        elif instruction == "]":
            if self.__cells.get() != 0:
                try:
                    openingBracketIndex = self.__openingBracketIndexes.pop(-1)
                except IndexError:
                    raise ValueError(
                        f"No opening bracket for loop on index: {self.__instructionPointer}"
                    )
                self.__instructionPointer = openingBracketIndex - 1
            else:
                self.__openingBracketIndexes.pop(-1)
        else:
            raise ValueError("Invalid characters detected.")

    def step(self):
        self.__interpret()
        self.__instructionPointer += 1

    def available(self):
        return not self.__instructionPointer >= len(self.__commands)
