# Credit - https://github.com/kying18/tic-tac-toe

from math import floor
from time import time

from numpy import inf

from src.utils.base_player import BasePlayer
from src.utils.funcs import minSecs


class TicTacToe:
    CROSS = "X"
    NOUGHT = "O"

    def __init__(self, player1=None, player2=None):
        self.__player1 = BasePlayer(playerType=self.CROSS, user=player1)
        self.__player2 = BasePlayer(playerType=self.NOUGHT, user=player2)
        self.__startTime = time()
        self.__winner = None
        self.__board = [" " for _ in range(9)]
        self.__currentPlayer = self.__player1

    def __checkWinner(self, slot: int, letter):
        if all([s == letter for s in self.__board[floor(slot / 3) * 3:(floor(slot / 3) + 1) * 3]]) \
                or all([s == letter for s in [self.__board[slot % 3 + i * 3] for i in range(3)]]):
            self.__winner = self.__currentPlayer
            return
        if not slot % 2:
            if all([s == letter for s in [self.__board[i] for i in [0, 4, 8]]]) \
                    or all([s == letter for s in [self.__board[i] for i in [2, 4, 6]]]):
                self.__winner = self.__currentPlayer

    def __switchPlayer(self):
        self.__currentPlayer = self.__player1 if self.__currentPlayer == self.__player2 else self.__player2

    def __computerMove(self, player, bot):
        otherPlayer = self.CROSS if player == self.NOUGHT else self.NOUGHT
        try:
            if self.__winner.getLetter() == otherPlayer:
                return [None, (1 if otherPlayer == bot else -1) * (self.getEmptySlots() + 1)]
        except:
            pass
        best = [None, -inf if player == bot else inf]
        for i, c in enumerate(self.__board):
             if c == " ":
                self.move(i + 1, computerSim=True)
                score = self.__computerMove(otherPlayer, bot)
                self.__board[i] = " "
                self.__winner = None
                self.__switchPlayer()
                score[0] = i
                if player == bot and score[1] > best[1] or player != bot and score[1] < best[1]:
                    best = score
        return best

    def move(self, slot, computerSim=False):
        try:
            slot = int(slot) - 1
        except:
            raise Exception("Invalid input.")
        if not 0 <= slot <= 8:
            raise Exception("Slot number must be 1-9 inclusive.")
        if self.__board[slot] != " ":
            raise Exception("This slot is already occupied!")
        self.__board[slot] = self.__currentPlayer.getPlayerType()
        self.__checkWinner(slot, self.__board[slot])
        if (self.__winner or not self.getEmptySlots()) and not computerSim:
            return
        self.__switchPlayer()
        if not self.__currentPlayer.getPlayer() and not computerSim:
            self.move(self.__computerMove(self.__currentPlayer.getPlayerType(), self.__currentPlayer.getPlayerType())[0] + 1)
            if not self.__currentPlayer.getPlayer():
                self.__switchPlayer()

    def displayBoard(self, numbers: bool=False):
        output = "Tic-Tac-Toe:\n\n"
        if numbers:
            board = [[str(i + 1) for i in range(j * 3, (j + 1) * 3)] for j in range(3)]
        else:
            board = [self.__board[i * 3:(i + 1) * 3] for i in range(3)]
        for row in board:
            output += "| " + " | ".join(row) + " |\n"
        return output[:-1]

    def getTime(self):
        return minSecs(time(), self.__startTime)

    def getEmptySlots(self):
        return self.__board.count(" ")

    def getCurrentPlayer(self):
        return self.__currentPlayer

    def getWinner(self):
        return self.__winner
