# Credit - https://github.com/kying18/tic-tac-toe

from math import floor, inf
from time import time

from other_utils.funcs import timeDifferenceStr


class TicTacToe:
    CROSS = "X"
    NOUGHT = "O"

    def __init__(self, player1=None, player2=None):
        self.__player1 = TicTacToePlayer(letter=self.CROSS, user=player1)
        self.__player2 = TicTacToePlayer(letter=self.NOUGHT, user=player2)
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

    def __computerMinimax(self, player, bot):
        otherPlayer = self.CROSS if player == self.NOUGHT else self.NOUGHT
        try:
            if self.__winner.getLetter() == otherPlayer:
                return [None, (1 if otherPlayer == bot else -1) * (self.getEmptySlots() + 1)]
            elif not self.getEmptySlots():
                return [None, 0]
        except:
            pass
        best = [None, -inf if player == bot else inf]
        for move in [i for i, j in enumerate(self.__board) if j == " "]:
            self.move(move + 1, computerSim=True)
            score = self.__computerMinimax(otherPlayer, bot)
            self.__board[move] = " "
            self.__winner = None
            self.__switchPlayer()
            score[0] = move
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
            raise Exception("Slot already occupied!")
        self.__board[slot] = self.__currentPlayer.getLetter()
        self.__checkWinner(slot, self.__board[slot])
        if self.__winner and not computerSim:
            return
        self.__switchPlayer()
        if not self.__currentPlayer.getPlayer() and not computerSim:
            self.move(self.__computerMinimax(self.__currentPlayer.getLetter(), self.__currentPlayer.getLetter())[0] + 1)
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
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s

    def getEmptySlots(self):
        return self.__board.count(" ")

    def getCurrentPlayer(self):
        return self.__currentPlayer.getPlayer()

    def getWinner(self):
        return self.__winner


class TicTacToePlayer:
    def __init__(self, letter: str, user=None):
        self.__letter = letter
        self.__player = user

    def getLetter(self):
        return self.__letter

    def getPlayer(self):
        return self.__player
