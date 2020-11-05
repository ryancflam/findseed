from random import choice
from time import time

from other_utils import funcs


class Hangman:
    def __init__(self):
        self.__hangmanpics = [
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
        self.__word = self.__randomWord()
        self.__dashes = str("-" * len(self.__word))
        self.__lives = 10
        self.__guesses = set()
        self.__start = time()
        
    def getWord(self):
        return self.__word
    
    def getDashes(self):
        return self.__dashes
    
    def getLives(self):
        return self.__lives
    
    def getTime(self):
        _, m, s, _ = funcs.timeDifferenceStr(time(), self.__start, noStr=True)
        return m, s

    def hangmanPic(self):
        return self.__hangmanpics[self.__lives]

    @staticmethod
    def __randomWord():
        with open(f"{funcs.getPath()}/game_models/hangman_words.txt","r") as f:
            lines = f.readlines()
        f.close()
        return choice(lines)[:-1]

    @staticmethod
    def __dash(secret, d, r):
        result = ""
        for i in range(len(secret)):
            if secret[i] == r:
                result += r
            else:
                result += d[i]
        return result

    def makeGuess(self, guess):
        if guess.lower() in self.__guesses:
            raise Exception("You have guessed this letter before.")
        elif guess.lower() in self.__word:
            self.__dashes = self.__dash(self.__word, self.__dashes, guess.lower())
            self.__guesses.add(guess.lower())
            return True
        else:
            self.__lives -= 1
            self.__guesses.add(guess.lower())
            return False
