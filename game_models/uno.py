from random import randint, shuffle
from time import time

from other_utils.funcs import timeDifferenceStr
from other_utils.item_cycle import ItemCycle


class Uno:
    def __init__(self):
        self.__startTime = None
        self.__gameEnd = False
        self.__winner = None
        self.__secondPlace = None
        self.__thirdPlace = None
        self.__fourthPlace = None
        self.__reverseMode = False
        self.__firstPlay = True
        self.__callout = False
        self.__playedWF = False
        self.__penalty = 0
        self.__playerList = []
        self.__playerHands = []
        self.__originalPlayerCount = 0
        self.__playerCycle = None
        self.__currentIndex = None
        self.__previousPlayer = None
        self.__colours = ["Blue", "Green", "Red", "Yellow"]
        self.__discardPile = []
        self.__deck = self.__createDeck()
        self.__validCards = self.__deck.copy()

    @staticmethod
    def __newColouredCard(colour, cardType):
        return f"{colour} {cardType}"

    @staticmethod
    def __getColour(colour):
        if colour.casefold().startswith("b"):
            return "Blue"
        if colour.casefold().startswith("g"):
            return "Green"
        if colour.casefold().startswith("y"):
            return "Yellow"
        if colour.casefold().startswith("r"):
            return "Red"
        if colour.casefold().startswith("w"):
            return "Wild"
        return None

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
        if not self.__deck:
            discard = self.__discardPile[-1]
            self.__discardPile.pop()
            self.__deck = self.__discardPile.copy()
            shuffle(self.__deck)
            self.__discardPile = [discard]
            if not self.__deck:
                return None
        card = self.__deck[randint(0, len(self.__deck) - 1)]
        handsObject.addCard(card)
        self.__deck.remove(card)
        return card

    def __getCardName(self, colour, cardType=None):
        colour = self.__getColour(colour) or colour
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

    def __calloutCheck(self):
        return len(self.__playerHands[self.__currentIndex].retrieveList()) == 1

    def __checkIfNoCardsLeft(self):
        if not self.__playerHands[self.__currentIndex].retrieveList():
            if not self.__winner:
                self.__winner = self.__playerList[self.__currentIndex]
            elif not self.__secondPlace:
                self.__secondPlace = self.__playerList[self.__currentIndex]
            elif not self.__thirdPlace:
                self.__thirdPlace = self.__playerList[self.__currentIndex]
            self.removePlayer(self.__playerList[self.__currentIndex], playedAllCards=True)
            self.__nextPlayer(True)
            if len(self.__playerList) == 1:
                if self.__originalPlayerCount == 2:
                    self.__secondPlace = self.__playerList[0]
                elif self.__originalPlayerCount == 3:
                    self.__thirdPlace = self.__playerList[0]
                elif self.__originalPlayerCount == 4:
                    self.__fourthPlace = self.__playerList[0]

    def __playReverse(self):
        self.__reverseMode = not self.__reverseMode

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
            if len(self.__playerList) > 2:
                self.__nextPlayer()
                if self.__firstPlay:
                    for _ in range(2):
                        self.__nextPlayer(True)
            else:
                if self.__firstPlay:
                    self.__nextPlayer(True)
        elif "+" in discard:
            if "+4" in discard and not self.__playedWF:
                self.__playedWF = True
                return None
            for _ in range(int(discard.split("+")[1]) + self.__penalty):
                drawnCards.append(self.__dealOne(self.__playerHands[self.__currentIndex]))
            self.__nextPlayer()
            self.__playedWF = False
        self.__penalty = 0
        self.__firstPlay = False
        return sorted(drawnCards)

    def addPlayer(self, player):
        self.__playerList.append(player)
        self.__playerHands.append(UnoPlayer())

    def removePlayer(self, player, playedAllCards=False):
        playerIndex = self.__playerList.index(player)
        if not playedAllCards:
            self.__originalPlayerCount -= 1
        del self.__playerList[playerIndex]
        del self.__playerHands[playerIndex]
        if len(self.__playerList) > 1:
            if self.__reverseMode:
                self.__playerCycle.previousItem()
            self.__currentIndex = self.__playerCycle.getIndex()
        else:
            self.__callout = False
            self.__gameEnd = True

    def startGame(self):
        self.__startTime = time()
        self.__playerCycle = ItemCycle(self.__playerList)
        self.__currentIndex = self.__playerCycle.getIndex()
        self.__firstDeal()
        self.__createDiscard()
        _ = self.__checkDiscard()
        self.__originalPlayerCount = len(self.__playerList.copy())

    def drawCard(self):
        drawnCards = []
        card = self.__dealOne(self.__playerHands[self.__currentIndex])
        if card is None:
            return None, None, False, False
        drawnCards.append(card)
        affectedPlayer = self.__playerList[self.__currentIndex]
        self.__nextPlayer()
        discard = self.__discardPile[-1]
        drawnCard = drawnCards[0]
        playable, wildCard = False, False
        if "Wild" in drawnCard or drawnCard.split(" ")[0] == discard.split(" ")[0] \
                or drawnCard.split(" ")[1] == discard.split(" ")[1]:
            playable = True
            if "Wild" in drawnCard:
                wildCard = True
        return sorted(drawnCards), affectedPlayer, playable, wildCard

    def saidUno(self):
        self.__callout = False

    def callout(self):
        if self.__callout:
            self.__nextPlayer(True)
            drawnCards = []
            for _ in range(2):
                drawnCards.append(self.__dealOne(self.__playerHands[self.__currentIndex]))
            self.__callout = False
            self.__nextPlayer()
            return sorted(drawnCards)
        return None

    def challengePlayer(self, challenge=False):
        if self.__playedWF:
            guilty = False
            if challenge:
                self.__nextPlayer(True)
                for card in self.getHand(self.__playerList[self.__currentIndex]):
                    if card.startswith("Wild"):
                        continue
                    else:
                        accuseColour = card.split(" ")[0]
                        discardColour = self.__discardPile[-2].split(" ")[0]
                        if discardColour == accuseColour:
                            guilty = True
                            break
                if not guilty:
                    self.__nextPlayer()
                    self.__penalty = 2
            affectedPlayer = self.__playerList[self.__currentIndex]
            return self.__checkDiscard(), affectedPlayer, guilty
        return None, None, False

    def playWildCard(self, colour, plusFour=False, playDrawn=False):
        if playDrawn:
            self.__nextPlayer(True)
        try:
            colour = self.__getColour(colour)
            if colour is None or colour == "Wild":
                raise Exception("Unknown colour.")
            card = f"Wild{' +4' if plusFour else ''}"
            self.__playerHands[self.__currentIndex].removeCard(card)
            card = f"{colour} {card.replace(' ', '')}"
            self.__discardPile.append(card)
            self.__callout = self.__calloutCheck()
            self.__checkIfNoCardsLeft()
            self.__previousPlayer = self.__playerList[self.__currentIndex]
            self.__nextPlayer()
            affectedPlayer = self.__playerList[self.__currentIndex]
            return self.__checkDiscard(), affectedPlayer, self.__callout
        except Exception as ex:
            raise Exception(str(ex))

    def playColouredCard(self, card, playDrawn=False):
        if playDrawn:
            self.__nextPlayer(True)
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
                self.__callout = self.__calloutCheck()
                self.__checkIfNoCardsLeft()
                self.__previousPlayer = self.__playerList[self.__currentIndex]
                self.__nextPlayer()
                affectedPlayer = self.__playerList[self.__currentIndex]
                return self.__checkDiscard(), affectedPlayer, self.__callout
            except Exception as ex:
                raise Exception(str(ex))
        else:
            raise Exception("You cannot play that card!")

    def getPlayerRanking(self):
        return self.__winner, self.__secondPlace, self.__thirdPlace, self.__fourthPlace

    def getDiscardPileCard(self):
        return self.__discardPile[-1]

    def getPlayerList(self):
        return self.__playerList

    def getCurrentPlayer(self):
        return self.__playerList[self.__currentIndex]

    def getPreviousPlayer(self):
        return self.__previousPlayer

    def getHand(self, player):
        return sorted(self.__playerHands[self.__playerList.index(player)].retrieveList())

    def getGameEndBool(self):
        return self.__gameEnd

    def getCallout(self):
        return self.__callout

    def getTime(self):
        _, m, s, _ = timeDifferenceStr(time(), self.__startTime, noStr=True)
        return m, s


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
