from other_utils.playing_cards import PlayingCards


class CardTrick:
    def __init__(self):
        self.__sample = PlayingCards().randomCard(21)

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
