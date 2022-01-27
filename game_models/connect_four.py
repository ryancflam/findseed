# Credit - https://gist.github.com/poke/6934842

from itertools import chain, groupby
from random import choice
from time import time

from other_utils.funcs import timeDifferenceStr

ROWS = 6
COLS = 7
EMOJIS = ":one: :two: :three: :four: :five: :six: :seven:"


class ConnectFour:
    NONE = "⬛ "
    RED = "🔴 "
    YELLOW = "🟡 "

    def __init__(self, player1=None, player2=None):
        self.__player1 = ConnectFourPlayer(colour=self.RED, user=player1)
        self.__player2 = ConnectFourPlayer(colour=self.YELLOW, user=player2)
        self.__startTime = time()
        self.__winner = None
        self.__board = [[self.NONE] * ROWS for _ in range(COLS)]
        self.__currentPlayer = self.__player1

    def __diagonalsPos(self):
        for di in ([(j, i - j) for j in range(COLS)] for i in range(COLS + ROWS - 1)):
            yield [self.__board[i][j] for i, j in di if 0 <= i < COLS and 0 <= j < ROWS]

    def __diagonalsNeg(self):
        for di in ([(j, i - COLS + j + 1) for j in range(COLS)] for i in range(COLS + ROWS - 1)):
            yield [self.__board[i][j] for i, j in di if 0 <= i < COLS and 0 <= j < ROWS]

    def __checkWinner(self):
        for line in chain(*(self.__board, zip(*self.__board), self.__diagonalsPos(), self.__diagonalsNeg())):
            for colour, group in groupby(line):
                if colour != self.NONE and len(list(group)) > 3:
                    self.__winner = self.__currentPlayer
                    return

    def __switchPlayer(self):
        self.__currentPlayer = self.__player1 if self.__currentPlayer == self.__player2 else self.__player2

    def __validColumns(self):
        return [i for i in range(COLS) if self.__board[i][0] == self.NONE]

    def __computerMove(self):
        return choice(self.__validColumns())

    def place(self, col):
        try:
            col = int(col) - 1
        except:
            raise Exception("Invalid input.")
        if not 0 <= col <= (COLS - 1):
            raise Exception(f"Slot number must be 1-{COLS} inclusive.")
        if col not in self.__validColumns():
            raise Exception("This column is full!")
        i = -1
        while self.__board[col][i] != self.NONE:
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
        output = f"{EMOJIS}\n"
        for i in range(ROWS):
            for j in range(COLS):
                output += self.__board[j][i]
            output += "\n"
        return output[:-1]

    def getTime(self):
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s

    def getEmptySlots(self):
        empty = 0
        for row in self.__board:
            empty += row.count(self.NONE)
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
