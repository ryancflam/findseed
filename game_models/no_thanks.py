from random import randrange, shuffle
from time import time

from other_utils.funcs import timeDifferenceStr
from other_utils.item_cycle import ItemCycle


class NoThanks:
    def __init__(self, playerList: list):
        self.__startTime = time()
        self.__gameEnd = False
        self.__deck = self.__newDeck()
        self.__playerList = self.__newPlayerList(list(filter(None, playerList)))
        self.__playerCycle = ItemCycle(self.__playerList)
        self.__currentPlayer = self.__playerList[0]
        self.__currentCardChips = 0
        self.__status = f"It is now {self.__currentPlayer.getPlayer().name}'s turn! The current card is {self.__deck[0]}. " + \
                        f'Would you like to take it, {self.__currentPlayer.getPlayer().name}? (Enter "sure" or "no thanks")'

    @staticmethod
    def __newDeck():
        cards = [i for i in range(3, 36)]
        for _ in range(9):
            cards.pop(randrange(len(cards)))
        shuffle(cards)
        return cards

    @staticmethod
    def __newPlayerList(rawPlayerList: list):
        newList = []
        for i in range(len(rawPlayerList)):
            newList.append(NoThanksPlayer(rawPlayerList[i], len(rawPlayerList), i))
        return newList

    def __nextPlayer(self, quitGame: bool=False):
        self.__playerCycle.nextItem()
        self.__currentPlayer = self.__playerList[self.__playerCycle.getIndex()]
        if quitGame:
            self.__playerCycle.previousItem()

    def turn(self, option: str):
        option = option.casefold().strip().replace(" ", "")
        if option == "nothanks":
            try:
                self.__currentPlayer.skipCard()
                self.__status = f"{self.__currentPlayer.getPlayer().name} skips the card and loses 1 chip."
                self.__currentCardChips += 1
                self.__nextPlayer()
                self.__status += f" It is now {self.__currentPlayer.getPlayer().name}'s turn! The current card is {self.__deck[0]}" + \
                                 f" with {self.__currentCardChips} chip{'' if self.__currentCardChips == 1 else 's'}. " + \
                                 f'Would you like to take it, {self.__currentPlayer.getPlayer().name}? (Enter "sure" or "no thanks")'
            except Exception as ex:
                raise Exception(str(ex))
        elif option == "sure":
            self.__currentPlayer.takeCard(self.__deck[0], self.__currentCardChips)
            self.__status = f"{self.__currentPlayer.getPlayer().name} takes the card and gains " + \
                            f"{self.__currentCardChips} chip{'' if self.__currentCardChips == 1 else 's'}."
            self.__currentCardChips = 0
            self.__deck.pop(0)
            if not self.__deck:
                self.__status += " There are no more cards left!"
                self.__gameEnd = True
            else:
                self.__status += f" The current card is {self.__deck[0]}. " + \
                                 f'Would you like to take it, {self.__currentPlayer.getPlayer().name}? (Enter "sure" or "no thanks")'
        elif option in ["quit", "leave", "exit"]:
            self.__status = f"{self.__currentPlayer.getPlayer().name} leaves the game."
            index = self.__currentPlayer.getIndex()
            self.__nextPlayer(quitGame=True)
            del self.__playerList[index]
            for i in range(index, len(self.__playerList)):
                self.__playerList[i].updateIndex()
            if len(self.__playerList) < 3:
                self.__status += " There are not enough players for this game!"
                self.__gameEnd = True
            else:
                self.__status += f" It is now {self.__currentPlayer.getPlayer().name}'s turn! The current card is {self.__deck[0]}" + \
                                 f" with {self.__currentCardChips} chip{'' if self.__currentCardChips == 1 else 's'}. " + \
                                 f'Would you like to take it, {self.__currentPlayer.getPlayer().name}? (Enter "sure" or "no thanks")'
        elif option in ["chip", "chips", "time"]:
            pass
        else:
            raise Exception('Unknown input! Please enter "no thanks" to skip the card or "sure" to take the card.')

    def rankPlayers(self):
        return sorted(self.__playerList, key=lambda x: x.calculateScore())

    def getDeck(self):
        return self.__deck

    def getPlayerList(self):
        return self.__playerList

    def getCurrentPlayer(self):
        return self.__currentPlayer

    def getPlayer(self, index):
        return self.__playerList[index]

    def getGameEndBool(self):
        return self.__gameEnd

    def getStatus(self):
        return self.__status

    def getTime(self):
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s


class NoThanksPlayer:
    def __init__(self, user, totalPlayers: int, index: int):
        self.__player = user
        self.__cards = []
        self.__chips = 11 if totalPlayers < 6 else 9 if totalPlayers == 6 else 7
        self.__index = index

    def takeCard(self, card: int, cardChips: int):
        self.__cards.append(card)
        self.__cards.sort()
        self.__chips += cardChips

    def skipCard(self):
        if self.__chips > 0:
            self.__chips -= 1
        else:
            raise Exception("You have no chips left!")

    def calculateScore(self):
        gaps = [[s, e] for s, e in zip(self.__cards, self.__cards[1:]) if s + 1 < e]
        edges = iter(self.__cards[:1] + sum(gaps, []) + self.__cards[-1:])
        total = 0
        for i in list(zip(edges, edges)):
            total += i[0]
        return total - self.__chips

    def getCards(self):
        return self.__cards

    def getChips(self):
        return self.__chips

    def getIndex(self):
        return self.__index

    def updateIndex(self):
        self.__index -= 1

    def getPlayer(self):
        return self.__player
