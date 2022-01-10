# Credit - https://github.com/kying18/tic-tac-toe

from math import floor, inf
from time import time

from other_utils.funcs import timeDifferenceStr


class TicTacToe:
    def __init__(self, player1=None, player2=None):
        self.__player1 = TicTacToePlayer(letter="X", user=player1)
        self.__player2 = TicTacToePlayer(letter="O", user=player2)
        self.__startTime = time()
        self.__winner = None
        self.__board = [" " for _ in range(9)]
        self.__currentPlayer = self.__player1

    def __checkWinner(self, slot: int, letter):
        if all([s == letter for s in self.__board[floor(slot / 3) * 3:(floor(slot / 3) + 1) * 3]]) \
                or all([s == letter for s in [self.__board[slot % 3 + i * 3] for i in range(3)]]):
            return True
        if not slot % 2:
            if all([s == letter for s in [self.__board[i] for i in [0, 4, 8]]]) \
                    or all([s == letter for s in [self.__board[i] for i in [2, 4, 6]]]):
                return True
        return False

    def __availableMoves(self):
        return [i for i, x in enumerate(self.__board) if x == " "]

    def __computer(self, player, bot):
        otherPlayer = "X" if player == "O" else "O"
        try:
            if self.__winner.getLetter() == otherPlayer:
                return {"pos": None,
                        "score": 1 * (self.getEmptySlots() + 1) if otherPlayer == bot else -1 * (self.getEmptySlots() + 1)}
            elif not self.getEmptySlots():
                return {"pos": None, "score": 0}
        except:
            pass
        if player == bot:
            best = {"pos": None, "score": -inf}
        else:
            best = {"pos": None, "score": inf}
        for move in self.__availableMoves():
            self.makeMove(move, computerSim=True)
            score = self.__computer(otherPlayer, bot)
            self.__board[move] = " "
            self.__winner = None
            self.__switchPlayer()
            score["pos"] = move
            if player == bot:
                if score["score"] > best["score"]:
                    best = score
            else:
                if score["score"] < best["score"]:
                    best = score
        return best

    def __switchPlayer(self):
        self.__currentPlayer = self.__player1 if self.__currentPlayer == self.__player2 else self.__player2

    def makeMove(self, slot, computerSim=False):
        try:
            slot = int(slot)
        except:
            return
        if not 0 <= slot <= 8:
            raise Exception("Out of bounds! Slot number must be 1-9 inclusive.")
        if self.__board[slot] != " ":
            raise Exception("Slot already occupied!")
        else:
            self.__board[slot] = self.__currentPlayer.getLetter()
            if self.__checkWinner(slot, self.__board[slot]):
                self.__winner = self.__currentPlayer
                if not computerSim:
                    return
            self.__switchPlayer()
            if not self.__currentPlayer.getPlayer() and not computerSim:
                self.makeMove(self.__computer(self.__currentPlayer.getLetter(), self.__currentPlayer.getLetter())["pos"])
                if not self.__currentPlayer.getPlayer():
                    self.__switchPlayer()

    def displayBoard(self, numbers: bool=False):
        output = "Current board:\n\n"
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
