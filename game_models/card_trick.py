from random import sample


class PlayingCards:
    def __init__(self):
        self.__number = ["A  ", "2  ", "3  ", "4  ", "5  ", "6  ", "7  ", "8  ", "9  ", "10 ", "J  ", "Q  ", "K  "]
        self.__suit = ["♠", "♦", "♥", "♣"]

    def getCards(self):
        return [x + y for y in self.__suit for x in self.__number]

    @staticmethod
    def returnCardName(card):
        card = str(card).replace(" ", "")
        cardName = " of "
        if card.startswith("1"):
            cardName = "10" + cardName
        else:
            try:
                number = int(card[:1])
                cardName = str(number) + cardName
            except:
                if card[:1] == "A":
                    cardName = "Ace" + cardName
                elif card[:1] == "J":
                    cardName = "Jack" + cardName
                elif card[:1] == "Q":
                    cardName = "Queen" + cardName
                else:
                    cardName = "King" + cardName
        if card.endswith("♠"):
            cardName += "Spades"
        elif card.endswith("♥"):
            cardName += "Hearts"
        elif card.endswith("♦"):
            cardName += "Diamonds"
        else:
            cardName += "Clubs"
        return cardName

    @staticmethod
    def returnCardImage(card):
        card = card.replace("10", "0").replace("♠", "S").replace("♦", "D")
        card = card.replace("♥", "H").replace("♣", "C").replace(" ", "")
        return f"https://deckofcardsapi.com/static/img/{card[:1]}{card[-1]}.png"


class CardTrick:
    def __init__(self):
        self.__sample = sample(PlayingCards().getCards(), 21)

    @staticmethod
    def piles(deck):
        p1 = deck[0::3]
        p2 = deck[1::3]
        p3 = deck[2::3]
        return p1, p2, p3

    @staticmethod
    def shuffle(choice, p1, p2, p3):
        deck = p1 + p3 + p2
        if choice == 1:
            deck = p2 + p1 + p3
        elif choice == 2:
            deck = p1 + p2 + p3
        return deck

    @staticmethod
    def showCards(p1, p2, p3):
        prst = "=======================\nPile 1: Pile 2: Pile 3:\n"
        for i in range(7):
            prst += p1[i] + "    " + p2[i] + "    " + p3[i] + "\n"
        prst += "======================="
        return prst

    @staticmethod
    def getCardNameImg(card):
        return PlayingCards().returnCardName(card), PlayingCards().returnCardImage(card)

    def getSample(self):
        return self.__sample
