from random import sample


class PlayingCards:
    def __init__(self):
        self.__number = [
            "A  ", "2  ", "3  ", "4  ", "5  ", "6  ", "7  ", "8  ", "9  ", "10 ", "J  ", "Q  ", "K  "
        ]
        self.__suit = ["♠", "♦", "♥", "♣"]
        self.__cards = [i + j for j in self.__suit for i in self.__number]

    def randomCard(self, amount: int=1):
        if not 1 <= amount <= 52:
            raise Exception("Amount must be 1-52 inclusive.")
        return sample(self.__cards, amount)

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
        card = card.replace("10", "0").replace("♠", "S").replace("♦", "D").replace("♥", "H").replace("♣", "C").replace(" ", "")
        return f"https://deckofcardsapi.com/static/img/{card[:1]}{card[-1]}.png"
