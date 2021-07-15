"""
File: gameinstance.py
This file contains the implementation of the GameInstance Class.

The GameInstance class is a container for all the states of the game, which
will be modified by the GameController Object of the game. All this class
will contain are helper methods to gather the data for the GameController to
process. This will also contain a few setter methods that have the sole purpose
of abstracting logic from the GameController object.
"""

from player import Player

class GameInstance:
    def __init__(self, 
        gamecode,
        maxHackers=1,
        maxWhitehats=1,
        maxInvestigators=1,
        aliasFilename="random_names.txt"):
        # Initialise GameInstance
        self.gamecode = gamecode
        self.players = []
        self.hackers = []
        self.whitehats = []
        self.investigators = []
        self.civilians = []

        self.spectators = []

        self.status = 0
        self.winner = 0

        self.maxHackers = maxHackers
        self.maxWhitehats = maxWhitehats
        self.maxInvestigators = maxInvestigators

        self.aliasFilename = aliasFilename

    def getPlayers(self):
        pass

    def getOnlinePlayers(self):
        pass

    def getOfflinePlayers(self):
        pass

    def getOnlinePlayersFromRole(self, roleName):
        pass


    def setPlayerStatus(self, playerName, status):
        pass

    def setPlayerRole(self, playerName, status):
        pass

    def setPlayerAlias(self, playerName, status):
        pass

    def getPlayerFromName(self, playerName) -> Player:
        pass

    def getPlayerFromAlias(self, playerAlias) -> Player:
        pass


    def getGameStatus(self) -> int:
        pass

    def getWinner(self) -> int:
        pass
