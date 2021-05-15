from random import randint
from time import time

from other_utils.funcs import timeDifferenceStr


class Minesweeper:
    def __init__(self):
        self.__grid = []
        self.__dispboard = []
        self.__row = 10
        self.__col = 10
        self.__mines = 10
        self.__startTime = time()
        self.__uncovered = 0
        self.__won = False
        self.__gameEnd = False
        self.__attempts = 0
        self.__placeMines()

    def __placeMines(self):
        self.__grid = [[0 for _ in range(self.__col)] for _ in range (self.__row)]
        self.__dispboard = [["." for _ in range(self.__col)] for _ in range(self.__row)]
        minePlacements = 0
        while minePlacements != self.__mines:
            mpCol = randint(0, self.__col - 1)
            mpRow = randint(0, self.__row - 1)
            if self.__grid[mpRow][mpCol] != -1:
                self.__grid[mpRow][mpCol] = -1
                minePlacements += 1
        for r in range(self.__row):
            for c in range(self.__col):
                minecount = 0
                if c > 0:
                    if self.__grid[r][c - 1] == -1:
                        minecount += 1
                    if r > 0:
                        if self.__grid[r - 1][c - 1] == -1:
                            minecount += 1
                if r > 0:
                    if self.__grid[r - 1][c] == -1:
                        minecount += 1
                    if c < self.__col - 1:
                        if self.__grid[r - 1][c + 1] == -1:
                            minecount += 1
                if c < self.__col - 1:
                    if self.__grid[r][c + 1] == -1:
                        minecount += 1
                    if r < self.__row - 1:
                        if self.__grid[r + 1][c + 1] == -1:
                            minecount += 1
                if r < self.__row - 1:
                    if self.__grid[r + 1][c] == -1:
                        minecount += 1
                    if c > 0:
                        if self.__grid[r + 1][c - 1] == -1:
                            minecount += 1
                if self.__grid[r][c] != -1:
                    self.__grid[r][c] = minecount

    def revealDots(self):
        xloc, yloc = 0, 0
        for x in self.__grid:
            for y in x:
                if y == -1:
                    self.__dispboard[xloc][yloc] = "●"
                yloc += 1
            xloc += 1
            yloc = 0
        self.__gameEnd = True

    def displayBoard(self):
        output = "  "
        for i in range(self.__col):
            output += " " + str(i)
        output += "\n   " + "-" * (self.__col * 2 - 1)
        for r in range(self.__row):
            s = str(r) + "|"
            for c in range(self.__col):
                s += " " + self.__dispboard[r][c]
            output += "\n" + s
        return output

    def getTime(self):
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s

    def getUncovered(self):
        return self.__uncovered

    def getGameEnd(self):
        return self.__gameEnd

    def getAttempts(self):
        return self.__attempts

    def getDispboard(self):
        return self.__dispboard

    def uncoverDots(self, xx, yy, player=True):
        if player:
            self.__attempts += 1
        if self.__dispboard[yy][xx] == "F":
            if player:
                self.__attempts -= 1
            return
        if self.__dispboard[yy][xx] != ".":
            if player:
                self.__attempts -= 1
            return
        if self.__grid[yy][xx] > 0:
            self.__dispboard[yy][xx] = str(self.__grid[yy][xx])
            return
        if not self.__grid[yy][xx]:
            self.__dispboard[yy][xx] = " "
            if xx > 0:
                if self.__grid[yy][xx - 1] >= 0:
                    self.uncoverDots(xx - 1, yy, player=False)
                if yy > 0:
                    if self.__grid[yy - 1][xx - 1] >= 0:
                        self.uncoverDots(xx - 1, yy - 1, player=False)
            if yy > 0:
                if self.__grid[yy - 1][xx] >= 0:
                    self.uncoverDots(xx, yy - 1, player=False)
                    if xx < self.__col - 1:
                        if self.__grid[yy - 1][xx + 1] >= 0:
                            self.uncoverDots(xx + 1, yy - 1, player=False)
            if xx < self.__col - 1:
                if self.__grid[yy][xx + 1] >= 0:
                    self.uncoverDots(xx + 1, yy, player=False)
                if yy < self.__row - 1:
                    if self.__grid[yy + 1][xx + 1] >= 0:
                        self.uncoverDots(xx + 1, yy + 1, player=False)
            if yy < self.__row - 1:
                if self.__grid[yy + 1][xx] >= 0:
                    self.uncoverDots(xx, yy + 1, player=False)
                if xx > 0:
                    if self.__grid[yy + 1][xx - 1] >= 0:
                       self.uncoverDots(xx - 1, yy + 1, player=False)
            return
        if self.__grid[yy][xx] == -1:
            if self.__attempts == 1:
                while self.__grid[yy][xx] == -1:
                    self.__placeMines()
                self.uncoverDots(xx, yy)
                self.__attempts -= 1
                return
            self.__dispboard[yy][xx] = "●"
            xloc = 0
            yloc = 0
            self.__gameEnd = True
            for x in self.__grid:
                for y in x:
                    if y == -1:
                        self.__dispboard[xloc][yloc] = "●"
                    yloc += 1
                xloc += 1
                yloc = 0
            return

    def winLose(self):
        self.__uncovered = 0
        for i in range(self.__row):
            for u in range(self.__col):
                if self.__dispboard[i][u] != "." and self.__dispboard[i][u] != "F" and self.__dispboard[i][u] != "●":
                    self.__uncovered += 1
                if self.__dispboard[i][u] == "●":
                    return self.__won
        if self.__row * self.__col - self.__mines == self.__uncovered:
            xloc = 0
            yloc = 0
            for x in self.__grid:
                for y in x:
                    if y == -1:
                        self.__dispboard[xloc][yloc] = "●"
                    yloc += 1
                xloc += 1
                yloc = 0
            self.__won = True
            self.__gameEnd = True
        return self.__won
