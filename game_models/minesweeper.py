from time import time
from random import randint

import funcs


class Minesweeper:
    def __init__(self):
        self.__grid = []
        self.__dispboard = []
        self.__row = 10
        self.__col = 10
        self.__mines = 10
        self.__start = time()
        self.__uncovered = 0
        self.__won = False
        self.__gameEnd = False
        self.__attempts = 0
        self.__createBoard()

    def __createBoard(self):
        for r in range(self.__row):
            self.__grid.append([])
            for c in range(self.__col):
                self.__grid[r].append(0)
        for r in range(self.__row):
            self.__dispboard.append([])
            for c in range(self.__col):
                self.__dispboard[r].append(".")
        mp = 0
        while mp != self.__mines:
            mpc = randint(0, self.__col-1)
            mpr = randint(0, self.__row-1)
            if self.__grid[mpr][mpc] != -1:
                self.__grid[mpr][mpc] =- 1
                mp += 1
        for r in range(self.__row):
            for c in range(self.__col):
                minecount = 0
                if c>0:
                    if self.__grid[r][c-1] == -1:
                        minecount += 1
                    if r > 0:
                        if self.__grid[r-1][c-1] == -1:
                            minecount += 1
                if r > 0:
                    if self.__grid[r-1][c] == -1:
                        minecount += 1
                    if c < self.__col-1:
                        if self.__grid[r-1][c+1] == -1:
                            minecount += 1
                if c < self.__col-1:
                    if self.__grid[r][c+1] == -1:
                        minecount += 1
                    if r < self.__row-1:
                        if self.__grid[r+1][c+1] == -1:
                            minecount += 1
                if r < self.__row-1:
                    if self.__grid[r+1][c] == -1:
                        minecount += 1
                    if c > 0:
                        if self.__grid[r+1][c-1] == -1:
                            minecount += 1
                if self.__grid[r][c] != -1:
                    self.__grid[r][c] = minecount

    def revealSquares(self):
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
        st = "  "
        for i in range(self.__col):
            st += " " + str(i)
        st += "\n   -------------------"
        for r in range(self.__row):
            s = str(r) + "|"
            for c in range(self.__col):
                s += " " + self.__dispboard[r][c]
            st += "\n" + s
        return st

    def getTime(self):
        _, m, s, _ = funcs.timeDifferenceStr(time(), self.__start, noStr=True)
        return m, s

    def getUncovered(self):
        return self.__uncovered

    def getGameEnd(self):
        return self.__gameEnd

    def getAttempts(self):
        return self.__attempts

    def getDispboard(self):
        return self.__dispboard

    def incrementAttempts(self):
        self.__attempts += 1

    def uncoverSquares(self, xx, yy):
        if self.__dispboard[yy][xx] == "F":
            return
        if self.__dispboard[yy][xx] != ".":
            return
        if self.__grid[yy][xx] > 0:
            self.__dispboard[yy][xx] = str(self.__grid[yy][xx])
            return
        if self.__grid[yy][xx] == 0:
            self.__dispboard[yy][xx] = " "
            if xx > 0:
                if self.__grid[yy][xx-1] >= 0:
                    self.uncoverSquares(xx-1, yy)
                if yy > 0:
                    if self.__grid[yy-1][xx-1] >= 0:
                        self.uncoverSquares(xx-1, yy-1)
            if yy > 0:
                if self.__grid[yy-1][xx] >= 0:
                    self.uncoverSquares(xx, yy-1)
                    if xx < self.__col-1:
                        if self.__grid[yy-1][xx+1] >= 0:
                            self.uncoverSquares(xx+1, yy-1)
            if xx < self.__col-1:
                if self.__grid[yy][xx+1] >= 0:
                    self.uncoverSquares(xx+1, yy)
                if yy < self.__row-1:
                    if self.__grid[yy+1][xx+1] >= 0:
                        self.uncoverSquares(xx+1, yy+1)
            if yy < self.__row-1:
                if self.__grid[yy+1][xx] >= 0:
                    self.uncoverSquares(xx, yy+1)
                if xx > 0:
                    if self.__grid[yy+1][xx-1] >= 0:
                       self.uncoverSquares(xx-1, yy+1)
            return
        if self.__grid[yy][xx] == -1:
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
