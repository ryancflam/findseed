from random import choice
from time import time

from other_utils.funcs import minSecs, readTxt


class Hangman:
    HANGMAN_STATES = [
        "┌----\n|   |\n|   O\n| / | \\\n|   |\n|  / \\\n| /   \\\n|\n| Over!\n└-------",
        "┌----\n|   |\n|   O\n| / | \\\n|   |\n|  / \\\n| /\n|\n|1 life\n└-------",
        "┌----\n|   |\n|   O\n| / | \\\n|   |\n|  /\n| /\n|\n|2 lives\n└-------",
        "┌----\n|   |\n|   O\n| / | \\\n|   |\n|  /\n|\n|\n|3 lives\n└-------",
        "┌----\n|   |\n|   O\n| / | \\\n|   |\n|\n|\n|\n|4 lives\n└-------",
        "┌----\n|   |\n|   O\n| / | \\\n|\n|\n|\n|\n|5 lives\n└-------",
        "┌----\n|   |\n|   O\n| / |\n|\n|\n|\n|\n|6 lives\n└-------",
        "┌----\n|   |\n|   O\n|   |\n|\n|\n|\n|\n|7 lives\n└-------",
        "┌----\n|   |\n|   O\n|\n|\n|\n|\n|\n|8 lives\n└-------",
        "┌----\n|   |\n|\n|\n|\n|\n|\n|\n|9 lives\n└-------"
    ]

    def __init__(self, client):
        self.__client = client
        self.__client.loop.create_task(self.__newWord())
        self.__dashes = None
        self.__lives = 10
        self.__guesses = set()
        self.__startTime = time()

    async def __newWord(self):
        self.__word = choice((await readTxt("assets/chat_games/hangman_words.txt", lines=True)))
        self.__dashes = str("-" * len(self.__word))

    @staticmethod
    def __dash(secret, d, r):
        result = ""
        for i in range(len(secret)):
            result += r if secret[i] == r else d[i]
        return result

    def getWord(self):
        return self.__word
    
    def getDashes(self):
        return self.__dashes
    
    def getLives(self):
        return self.__lives
    
    def getTime(self):
        return minSecs(time(), self.__startTime)

    def hangmanPic(self):
        return self.HANGMAN_STATES[self.__lives]

    def makeGuess(self, guess):
        if guess.lower() in self.__guesses:
            raise Exception("You have already guessed this letter!")
        elif guess.lower() in self.__word:
            self.__dashes = self.__dash(self.__word, self.__dashes, guess.lower())
            self.__guesses.add(guess.lower())
            return True
        else:
            self.__lives -= 1
            self.__guesses.add(guess.lower())
            return False
