from random import sample
from time import time

from other_utils.funcs import replaceCharacters, timeDifferenceStr


class BullsAndCows:
    def __init__(self):
        self.__startTime = time()
        self.__attempts = 0
        self.__number = "".join(map(str, sample(range(1, 10), 4)))
        self.__gameEnd = False

    def getNumber(self, sep=False):
        return self.__number if not sep else "-".join(self.__number)

    def getAttempts(self):
        return self.__attempts

    def getGameEnd(self):
        return self.__gameEnd

    def getTime(self):
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s

    def guess(self, value: str):
        value = replaceCharacters(value, [" ", ",", "-"]).casefold()
        if value == "quit" or value == "exit" or value == "stop":
            self.__gameEnd = True
            return 0, 0
        if value == "help" or value == "time":
            return 0, 0
        try:
            _ = int(value)
        except ValueError:
            raise Exception("Invalid characters found.")
        if len(value) != 4:
            raise Exception("Number must contain exactly four digits.")
        if len(set(value)) != 4:
            raise Exception("Duplicate characters found.")
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
            self.__gameEnd = True
        return bulls, cows
