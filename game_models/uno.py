# WIP NOT DONE YET

from time import time
from random import randint, shuffle

from other_utils import funcs


class Cycle:
    def __init__(self, cycle):
        self.__cycle = cycle
        self.__index = 0

    def getIndex(self):
        return self.__index

    def getItem(self):
        try:
            return self.__cycle[self.__index]
        except IndexError:
            self.__index = 0
            return self.__cycle[self.__index]

    def nextItem(self):
        self.__index += 1
        if self.__index >= len(self.__cycle):
            self.__index = 0

    def previousItem(self):
        self.__index -= 1
        if self.__index < 0:
            self.__index = len(self.__cycle) - 1

    def removeItem(self):
        del self.__cycle[self.__index]


class UnoPlayer:
    def __init__(self):
        self.__cards = []

    def addCard(self, card):
        self.__cards.append(card)

    def removeCard(self, card):
        try:
            self.__cards.remove(card)
        except ValueError:
            raise Exception("You do not have that card!")

    def retrieveList(self):
        return self.__cards


class Uno:
    def __init__(self):
        self.__startTime = None
        self.__gameEnd = False
        self.__reverseMode = False
        self.__callout = False
        self.__playerList = []
        self.__playerHands = []
        self.__playerCycle = None
        self.__currentIndex = None
        self.__colours = ["Blue", "Green", "Red", "Yellow"]
        self.__discardPile = []
        self.__deck = self.__createDeck()
        self.__validCards = self.__deck.copy()

    def addPlayer(self, player):
        self.__playerList.append(player)
        self.__playerHands.append(UnoPlayer())

    def removePlayer(self, player):
        playerIndex = self.__playerList.index(player)
        del self.__playerList[playerIndex]
        del self.__playerHands[playerIndex]
        self.__playerCycle.removeItem()
        if len(self.__playerList) > 1:
            if self.__reverseMode:
                self.__playerCycle.previousItem()
            self.__currentIndex = self.__playerCycle.getIndex()
        else:
            self.__gameEnd = True

    def startGame(self):
        self.__startTime = time()
        self.__playerCycle = Cycle(self.__playerList)
        self.__currentIndex = self.__playerCycle.getIndex()
        self.__firstDeal()
        self.__createDiscard()
        _ = self.__checkDiscard()

    @staticmethod
    def __newColouredCard(colour, cardType):
        return f"{colour} {cardType}"

    def __createDeck(self):
        deck = []
        for i in range(13):
            for colour in self.__colours:
                if i == 10:
                    for _ in range(2):
                        deck.append(self.__newColouredCard(colour, "+2"))
                elif i == 11:
                    for _ in range(2):
                        deck.append(self.__newColouredCard(colour, "Reverse"))
                elif i == 12:
                    for _ in range(2):
                        deck.append(self.__newColouredCard(colour, "Skip"))
                else:
                    deck.append(self.__newColouredCard(colour, str(i)))
                    if i != 0:
                        deck.append(self.__newColouredCard(colour, str(i)))
        for i in range(8):
            deck.append(f"Wild{' +4' if i < 4 else ''}")
        shuffle(deck)
        return deck

    def __createDiscard(self):
        x = randint(0, len(self.__deck) - 1)
        self.__discardPile.append(self.__deck[x])
        if self.__discardPile[-1] == "Wild +4":
            self.__createDiscard()
        else:
            self.__deck.remove(self.__deck[x])

    def __firstDeal(self):
        for _ in range(7):
            for handsObject in self.__playerHands:
                _ = self.__dealOne(handsObject)

    def __dealOne(self, handsObject):
        if len(self.__deck) == 0:
            return None
        card = self.__deck[randint(0, len(self.__deck) - 1)]
        handsObject.addCard(card)
        self.__deck.remove(card)
        return card

    def drawCard(self):
        drawnCards = []
        card = self.__dealOne(self.__playerHands[self.__currentIndex])
        if card is None:
            return None
        drawnCards.append(card)
        affectedPlayer = self.__playerList[self.__currentIndex]
        self.__nextPlayer()
        discard = self.__discardPile[-1]
        drawnCard = drawnCards[0]
        wildCard = False
        if drawnCard.contains("Wild") or drawnCard.split(" ")[0] == discard.split(" ")[0] \
                or drawnCard.split(" ")[1] == discard.split(" ")[1]:
            playable = True
            if drawnCard.contains("Wild"):
                wildCard = True
        else:
            playable = False
        return drawnCards, affectedPlayer, playable, wildCard

    def __getCardName(self, colour, cardType=None):
        if colour.casefold().startswith("b"):
            colour = "Blue"
        if colour.casefold().startswith("g"):
            colour = "Green"
        if colour.casefold().startswith("y"):
            colour = "Yellow"
        if colour.casefold().startswith("r"):
            colour = "Red"
        if colour.casefold().startswith("w"):
            colour = "Wild"
        if colour != "Wild" and cardType is None:
            return None
        if cardType is None:
            cardType = ""
        else:
            if cardType.casefold().startswith("r"):
                cardType = " Reverse"
            elif cardType.casefold().startswith("s"):
                cardType = " Skip"
            elif cardType.casefold().startswith("+"):
                drawValue = cardType[-1:]
                cardType = " +" + drawValue
            else:
                try:
                    cardType = int(cardType)
                    cardType = " " + str(cardType)
                except ValueError:
                    return None
        try:
            card = f"{colour}{cardType}"
            _ = self.__validCards.index(card)
            return card
        except ValueError:
            return None

    def saidUno(self):
        self.__callout = False

    def callout(self):
        if self.__callout:
            self.__nextPlayer(True)
            drawnCards = []
            for _ in range(2):
                drawnCards.append(self.__dealOne(self.__playerHands[self.__currentIndex]))
            self.__callout = False
            return drawnCards
        return None

    def __checkIfLastCard(self):
        return len(self.__playerHands[self.__currentIndex].retrieveList()) == 1

    def playWildCard(self, colour, plusFour=False):
        try:
            if colour.casefold().startswith("b"):
                colour = "Blue"
            elif colour.casefold().startswith("g"):
                colour = "Green"
            elif colour.casefold().startswith("y"):
                colour = "Yellow"
            elif colour.casefold().startswith("r"):
                colour = "Red"
            else:
                raise Exception("Unknown colour.")
            card = f"Wild{' +4' if plusFour else ''}"
            self.__playerHands[self.__currentIndex].removeCard(card)
            card = f"{colour} {card.replace(' ', '')}"
            self.__discardPile.append(card)
            self.__callout = self.__checkIfLastCard()
            self.__nextPlayer()
            affectedPlayer = self.__playerList[self.__currentIndex]
            return self.__checkDiscard(), affectedPlayer, self.__callout
        except Exception as ex:
            raise Exception(str(ex))

    def playColouredCard(self, card):
        discard = self.__discardPile[-1]
        card = card.casefold().replace(":", " ").replace("_", " ").replace("-", " ")
        try:
            colour, value = card.split(" ")
            card = self.__getCardName(colour, value)
            if card is None:
                raise Exception("Invalid card. Please check your spelling.")
        except IndexError:
            raise Exception("Invalid card. Please add a space between the colour and the value.")
        if discard == "Wild" or colour.casefold()[:1] == discard.casefold()[:1] \
                or value.casefold()[:1] == discard.split(" ")[1].casefold()[:1]:
            try:
                self.__playerHands[self.__currentIndex].removeCard(card)
                self.__discardPile.append(card)
                self.__callout = self.__checkIfLastCard()
                self.__nextPlayer()
                affectedPlayer = self.__playerList[self.__currentIndex]
                return self.__checkDiscard(), affectedPlayer, self.__callout
            except Exception as ex:
                raise Exception(str(ex))
        else:
            raise Exception("You cannot play that card!")

    def __playReverse(self):
        if self.__reverseMode:
            self.__reverseMode = False
        else:
            self.__reverseMode = True

    def __nextPlayer(self, backward=False):
        if self.__reverseMode and not backward or not self.__reverseMode and backward:
            self.__playerCycle.previousItem()
        else:
            self.__playerCycle.nextItem()
        self.__currentIndex = self.__playerCycle.getIndex()

    def __checkDiscard(self):
        discard = self.__discardPile[-1]
        drawnCards = []
        if discard.endswith("Skip"):
            self.__nextPlayer()
        elif discard.endswith("Reverse"):
            self.__playReverse()
            self.__nextPlayer()
        elif "+" in discard:
            for _ in range(int(discard.split("+")[1])):
                drawnCards.append(self.__dealOne(self.__playerHands[self.__currentIndex]))
            self.__nextPlayer()
        return drawnCards

    def getDiscardPileCard(self):
        return self.__discardPile[-1]

    def getTotalDrawableCards(self):
        return len(self.__deck)

    def getPlayerList(self):
        return self.__playerList

    def getCurrentPlayer(self):
        return self.__playerList[self.__currentIndex]

    def getHand(self, player):
        return self.__playerHands[self.__playerList.index(player)].retrieveList()

    def getGameEndBool(self):
        return self.__gameEnd

    def getTime(self):
        _, m, s, _ = funcs.timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s
