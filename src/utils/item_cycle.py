class ItemCycle:
    def __init__(self, cycle):
        self.__cycle = cycle
        self.__index = 0

    def getIndex(self):
        try:
            _ = self.__cycle[self.__index]
        except IndexError:
            self.__index = 0
        return self.__index

    def nextItem(self):
        self.__index += 1
        if self.__index >= len(self.__cycle):
            self.__index = 0

    def previousItem(self):
        self.__index -= 1
        if self.__index < 0:
            self.__index = len(self.__cycle) - 1

    def updateIndex(self, index):
        if 0 <= index <= len(self.__cycle) - 1:
            self.__index = index
