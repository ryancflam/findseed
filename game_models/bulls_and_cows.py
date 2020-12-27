from time import time
from random import sample

from other_utils.funcs import timeDifferenceStr


class BullsAndCows:
    def __init__(self):
        self.__startTime = time()
        self.__attempts = 0
        self.__number = "".join(map(str, sample(range(1, 10), 4)))
        self.__stopped = False

    def getNumber(self):
        return self.__number

    def getAttempts(self):
        return self.__attempts

    def getStoppedBool(self):
        return self.__stopped

    def getTime(self):
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s

    def guess(self, value: str):
        value = value.replace(" ", "")
        if value.casefold() == "quit" or value.casefold() == "exit" or value.casefold() == "stop":
            self.__stopped = True
            return 0, 0
        if value.casefold() == "help" or value.casefold() == "time":
            return 0, 0
        if len(value) != 4:
            raise Exception("Number must contain exactly four digits.")
        try:
            aa, bb, cc, dd = int(value[0]), int(value[1]), int(value[2]), int(value[3])
        except ValueError:
            raise Exception("Invalid characters found.")
        if aa == bb or aa == cc or aa == dd or bb == cc or bb == dd or cc == dd:
            raise Exception("Duplicates found.")
        bulls, cows = 0, 0
        for i in value:
            for j in self.__number:
                if i == j:
                    if value.index(i) == self.__number.index(j):
                        bulls += 1
                    else:
                        cows += 1
        self.__attempts += 1
        if bulls == 4:
            self.__stopped = True
        return bulls, cows
