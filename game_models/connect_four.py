# Credit - https://gist.github.com/rex8312/c7640c96430af5209e1a

from itertools import chain, groupby
from random import choice
from time import time

from other_utils.funcs import timeDifferenceStr


class ConnectFour:
    EMPTY = "⬛ "
    RED = "🔴 "
    YELLOW = "🟡 "

    def __init__(self, player1=None, player2=None):
        self.__player1 = ConnectFourPlayer(colour=self.RED, user=player1)
        self.__player2 = ConnectFourPlayer(colour=self.YELLOW, user=player2)
        self.__startTime = time()
        self.__winner = None
        self.__board = [[self.EMPTY] * 6 for _ in range(7)]
        self.__currentPlayer = self.__player1

    def __diagonalsPos(self, cols: int=7, rows: int=6):
        for di in ([(j, i - j) for j in range(cols)] for i in range(cols + rows -1)):
            yield [self.__board[i][j] for i, j in di if 0 <= i < cols and 0 <= j < rows]

    def __diagonalsNeg(self, cols: int=7, rows: int=6):
        for di in ([(j, i - cols + j + 1) for j in range(cols)] for i in range(cols + rows - 1)):
            yield [self.__board[i][j] for i, j in di if 0 <= i < cols and 0 <= j < rows]

    def __checkWinner(self):
        for line in chain(*(self.__board, zip(*self.__board), self.__diagonalsPos(), self.__diagonalsNeg())):
            for colour, group in groupby(line):
                if colour != self.EMPTY and len(list(group)) > 3:
                    self.__winner = self.__currentPlayer
                    return

    def __switchPlayer(self):
        self.__currentPlayer = self.__player1 if self.__currentPlayer == self.__player2 else self.__player2

    def __validColumns(self):
        return [i for i in range(7) if self.__board[i][0] == self.EMPTY]

    def __computerMove(self):
        return choice(self.__validColumns())

    def place(self, col):
        try:
            col = int(col) - 1
        except:
            raise Exception("Invalid input.")
        if not 0 <= col <= 6:
            raise Exception("Slot number must be 1-7 inclusive.")
        if col not in self.__validColumns():
            raise Exception("This column is full!")
        i = -1
        while self.__board[col][i] != self.EMPTY:
            i -= 1
        self.__board[col][i] = self.__currentPlayer.getColour()
        self.__checkWinner()
        if self.__winner:
            return
        self.__switchPlayer()
        if not self.__currentPlayer.getPlayer():
            self.place(self.__computerMove() + 1)
            if not self.__currentPlayer.getPlayer():
                self.__switchPlayer()

    def displayBoard(self):
        output = ":one: :two: :three: :four: :five: :six: :seven:\n"
        for i in range(6):
            for j in range(7):
                output += self.__board[j][i]
            output += "\n"
        return output[:-1]

    def getTime(self):
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s

    def getEmptySlots(self):
        empty = 0
        for row in self.__board:
            empty += row.count(self.EMPTY)
        return empty

    def getCurrentPlayer(self):
        return self.__currentPlayer.getPlayer()

    def getWinner(self):
        return self.__winner


class ConnectFourPlayer:
    def __init__(self, colour: str, user=None):
        self.__colour = colour
        self.__player = user

    def getColour(self):
        return self.__colour

    def getPlayer(self):
        return self.__player
