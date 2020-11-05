from time import time
from random import randint

import funcs


class Battleship:
    def __init__(self):
        self.__size = 10
        self.__carrier = 5
        self.__battleship = 4
        self.__cruiser = 3
        self.__submarine = 3
        self.__destroyer = 2
        self.__ships = 5
        self.__shipcode = ["S", "A", "B", "C", "D"]
        self.__shipsize = [self.__cruiser, self.__carrier, self.__battleship, self.__cruiser, self.__destroyer]
        self.__totalx = self.__cruiser + self.__carrier + self.__battleship + self.__cruiser + self.__destroyer
        self.__attempts = 0
        self.__start = time()
        self.__gameWon = False
        self.__board = self.__createBoard()
        self.__placeShips()

    def __createBoard(self):
        board = []
        for r in range(self.__size):
            board.append([])
            for c in range(self.__size):
                board[r].append(".")
        return board

    def __placeShips(self):
        for i in range(len(self.__shipcode)):
            done = False
            while not done:
                rand1 = randint(0, self.__size-1)
                rand2 = randint(0, self.__size-1)
                direction = randint(0, 2)
                piece = 0
                problem = False
                while piece < self.__shipsize[i] and not problem:
                    if self.__board[rand1][rand2] == ".":
                        self.__board[rand1][rand2] = self.__shipcode[i]
                    else:
                        problem = True
                    if direction == 0:
                        rand1 += 1
                    else:
                        rand2 += 1
                    if rand1 > self.__size-1 or rand2 > self.__size-1:
                        problem = True
                    else:
                        piece += 1
                    if problem:
                        for row in range(self.__size):
                            for column in range(self.__size):
                                if self.__board[row][column] == self.__shipcode[i]:
                                    self.__board[row][column] = "."
                if piece == self.__shipsize[i] and not problem:
                    done = True

    def displayBoard(self, showships):
        st = "Current board:\n\n   0 1 2 3 4 5 6 7 8 9\n   -------------------\n"
        for i in range(self.__size):
            st += f"{i}|"
            for j in range(self.__size):
                if showships:
                    st += f" {self.__board[i][j]}"
                    try:
                        st = st.replace("M", ".")
                    except:
                        pass
                else:
                    if self.__board[i][j] == "M":
                        st+=" M"
                    elif self.__board[i][j] == "X":
                        st += " X"
                    else:
                        st += " ."
            st += "\n"
        return st

    def getTime(self):
        _, m, s, _ = funcs.timeDifferenceStr(time(), self.__start, noStr=True)
        return m, s
    
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
                if self.__battleship == 0:
                    self.__ships -= 1
                    msg = "sunk the Battleship"
            if self.__board[row][col] == "S":
                self.__submarine -= 1
                if self.__submarine == 0:
                    self.__ships -= 1
                    msg = "sunk the Submarine"
            if self.__board[row][col] == "C":
                self.__cruiser -= 1
                if self.__cruiser == 0:
                    self.__ships -= 1
                    msg = "sunk the Cruiser"
            if self.__board[row][col] == "D":
                self.__destroyer -= 1
                if self.__destroyer == 0:
                    self.__ships -= 1
                    msg = "sunk the Destroyer"
            if self.__board[row][col] == "A":
                self.__carrier -= 1
                if self.__carrier == 0:
                    self.__ships -= 1
                    msg = "sunk the Aircraft Carrier"
            self.__board[row][col] = "X"
            if self.__totalx == 0:
                self.__gameWon = True
        self.__attempts += 1
        return msg
