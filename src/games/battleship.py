from random import randint
from time import time

from numpy import array

from src.utils.funcs import minSecs


class Battleship:
    def __init__(self):
        self.__boardSize = 10
        self.__carrier = 5
        self.__battleship = 4
        self.__cruiser = 3
        self.__submarine = 3
        self.__destroyer = 2
        self.__shipcode = ["S", "A", "B", "C", "D"]
        self.__shipsize = [
            self.__cruiser,
            self.__carrier,
            self.__battleship,
            self.__cruiser,
            self.__destroyer
        ]
        self.__ships = len(self.__shipcode)
        self.__totalx = sum(self.__shipsize)
        self.__attempts = 0
        self.__startTime = time()
        self.__gameWon = False
        self.__board = array([["." for _ in range(self.__boardSize)] for _ in range(self.__boardSize)])
        self.__placeShips()

    def __placeShips(self):
        for i, j in enumerate(self.__shipcode):
            while True:
                rand1 = randint(0, self.__boardSize - 1)
                rand2 = randint(0, self.__boardSize - 1)
                direction = randint(0, 2)
                piece = 0
                problem = False
                while piece < self.__shipsize[i] and not problem:
                    if self.__board[rand1][rand2] == ".":
                        self.__board[rand1][rand2] = j
                    else:
                        problem = True
                    if not direction:
                        rand1 += 1
                    else:
                        rand2 += 1
                    if rand1 > self.__boardSize - 1 or rand2 > self.__boardSize - 1:
                        problem = True
                    else:
                        piece += 1
                    if problem:
                        for r in range(self.__boardSize):
                            for c in range(self.__boardSize):
                                if self.__board[r][c] == j:
                                    self.__board[r][c] = "."
                if piece == self.__shipsize[i] and not problem:
                    break

    def displayBoard(self, showships=False):
        output = "Current board:\n\n  "
        for i in range(self.__boardSize):
            output += " " + str(i)
        output += "\n   " + "-" * (self.__boardSize * 2 - 1) + "\n"
        for i in range(self.__boardSize):
            output += f"{i}|"
            for j in range(self.__boardSize):
                if showships:
                    output += f" {self.__board[i][j]}"
                    try:
                        output = output.replace("M", ".")
                    except:
                        pass
                else:
                    if self.__board[i][j] == "M":
                        output += " M"
                    elif self.__board[i][j] == "X":
                        output += " X"
                    else:
                        output += " ."
            output += "\n"
        return output

    def getTime(self):
        return minSecs(time(), self.__startTime)

    def getShipcount(self):
        return self.__ships

    def getAttempts(self):
        return self.__attempts

    def getWonBool(self):
        return self.__gameWon

    def takeTurn(self, row, col):
        if self.__board[row][col] == "M" or self.__board[row][col] == "X":
            msg = "wasted a turn"
        elif self.__board[row][col] == ".":
            self.__board[row][col] = "M"
            msg = "missed"
        else:
            msg = "hit"
            self.__totalx -= 1
            if self.__board[row][col] == "B":
                self.__battleship -= 1
                if not self.__battleship:
                    self.__ships -= 1
                    msg = "sunk the Battleship"
            if self.__board[row][col] == "S":
                self.__submarine -= 1
                if not self.__submarine:
                    self.__ships -= 1
                    msg = "sunk the Submarine"
            if self.__board[row][col] == "C":
                self.__cruiser -= 1
                if not self.__cruiser:
                    self.__ships -= 1
                    msg = "sunk the Cruiser"
            if self.__board[row][col] == "D":
                self.__destroyer -= 1
                if not self.__destroyer:
                    self.__ships -= 1
                    msg = "sunk the Destroyer"
            if self.__board[row][col] == "A":
                self.__carrier -= 1
                if not self.__carrier:
                    self.__ships -= 1
                    msg = "sunk the Aircraft Carrier"
            self.__board[row][col] = "X"
            if not self.__totalx:
                self.__gameWon = True
        self.__attempts += 1
        return msg
