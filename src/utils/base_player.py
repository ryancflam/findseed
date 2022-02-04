class BasePlayer:
    def __init__(self, playerType: str, user=None):
        self.__playerType = playerType
        self.__player = user

    def getPlayerType(self):
        return self.__playerType

    def getPlayer(self):
        return self.__player
