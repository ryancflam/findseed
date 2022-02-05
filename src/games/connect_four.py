# Credit - https://gist.github.com/poke/6934842

from itertools import chain, groupby
from math import inf
from time import time

from src.utils.base_player import BasePlayer
from src.utils.funcs import minSecs, numberEmojis

ROWS = 6
COLS = 7


class ConnectFour:
    NONE = "⬛"
    RED = "🔴"
    YELLOW = "🟡"

    def __init__(self, player1=None, player2=None):
        self.__player1 = BasePlayer(playerType=self.RED, user=player1)
        self.__player2 = BasePlayer(playerType=self.YELLOW, user=player2)
        self.__startTime = time()
        self.__winner = None
        self.__board = [[self.NONE] * ROWS for _ in range(COLS)]
        self.__currentPlayer = self.__player1
        self.__pseudoMove = (None, None)

    def __diagonals(self, pos=True):
        for di in ([(j, ((i - j) if pos else (i - COLS + j + 1))) for j in range(COLS)] for i in range(COLS + ROWS - 1)):
            yield [self.__board[i][j] for i, j in di if 0 <= i < COLS and 0 <= j < ROWS]

    def __checkInARow(self, val: int=4):
        for line in chain(*(self.__board, zip(*self.__board), self.__diagonals(), self.__diagonals(pos=False))):
            for colour, group in groupby(line):
                if colour != self.NONE and len(list(group)) >= val:
                    return True
        return False

    def __checkWinner(self):
        self.__winner = self.__currentPlayer if self.__checkInARow() else None

    def __switchPlayer(self):
        self.__currentPlayer = self.__player1 if self.__currentPlayer == self.__player2 else self.__player2

    def __validColumns(self):
        return [i for i in range(COLS) if self.__board[i][0] == self.NONE]

    def __resetMove(self, switch=False):
        self.__board[self.__pseudoMove[0]][self.__pseudoMove[1]] = self.NONE
        self.__pseudoMove = (None, None)
        if switch:
            self.__switchPlayer()

    def __computerMove(self):
        scores = {0: 0}
        for col in self.__validColumns():
            scores[col] = 0
            self.insert(col + 1, computerSim=True)
            if col == COLS // 2:
                scores[col] += 4
            if self.__winner:
                scores[col] += inf
                self.__winner = None
                self.__resetMove(switch=True)
                break
            elif self.__checkInARow(3):
                scores[col] += 5
            elif self.__checkInARow(2):
                scores[col] += 2
            self.__resetMove()
            self.insert(col + 1, computerSim=True)
            if self.__winner:
                scores[col] += inf
                self.__winner = None
            elif self.__checkInARow(3):
                scores[col] += 4
            elif self.__checkInARow(2):
                scores[col] += 2
            self.__resetMove()
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[0]

    def insert(self, col, computerSim=False):
        try:
            col = int(col) - 1
        except:
            raise Exception("Invalid input.")
        if not 0 <= col < COLS:
            raise Exception(f"Column number must be 1-{COLS} inclusive.")
        if col not in self.__validColumns():
            raise Exception("This column is full!")
        i = -1
        while self.__board[col][i] != self.NONE:
            i -= 1
        self.__board[col][i] = self.__currentPlayer.getPlayerType()
        if computerSim:
            self.__pseudoMove = (col, i)
        self.__checkWinner()
        if (self.__winner or not self.getEmptySlots()) and not computerSim:
            return
        self.__switchPlayer()
        if not self.__currentPlayer.getPlayer() and not computerSim:
            self.insert(self.__computerMove() + 1)

    def displayBoard(self):
        output = " ".join(numberEmojis()[i] for i in range(1, COLS + 1)) + "\n"
        for i in range(ROWS):
            output += " ".join(self.__board[j][i] for j in range(COLS)) + "\n"
        return output[:-1]

    def getTime(self):
        return minSecs(time(), self.__startTime)

    def getEmptySlots(self):
        empty = 0
        for row in self.__board:
            empty += row.count(self.NONE)
        return empty

    def getCurrentPlayer(self):
        return self.__currentPlayer

    def getWinner(self):
        return self.__winner
