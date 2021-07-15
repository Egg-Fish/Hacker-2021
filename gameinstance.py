"""
File: gameinstance.py
This file contains the implementation of the GameInstance Class.

The GameInstance class is a container for all the states of the game, which
will be modified by the GameController Object of the game. All this class
will contain are helper methods to gather the data for the GameController to
process. This will also contain a few setter methods that have the sole purpose
of abstracting logic from the GameController object.
"""
import random

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
        return self.players

    def getOnlinePlayers(self):
        result = list(filter(lambda obj: obj.getStatus() == "online", self.players))
        return result

    def getOfflinePlayers(self):
        result = list(filter(lambda obj: obj.getStatus() != "online", self.players))
        return result

    def getOnlinePlayersFromRole(self, roleName):
        onlineplayers = self.getOnlinePlayers()
        result = list(filter(lambda obj: obj.role == roleName, onlineplayers))
        return result


    def setPlayerStatus(self, playerName, status):
        for player in self.players:
            if player.getName() == playerName:
                player.setStatus(status)

    def setPlayerRole(self, playerName, role):
        for player in self.players:
            if player.getName() == playerName:
                player.setRole(role)

    def setPlayerAlias(self, playerName, alias):
        for player in self.players:
            if player.getName() == playerName:
                player.setAlias(alias)

    def getPlayerFromName(self, playerName) -> Player:
        for player in self.players:
            if player.getName() == playerName:
                return player

    def getPlayerFromAlias(self, playerAlias) -> Player:
        for player in self.players:
            if player.getAlias() == playerAlias:
                return player

    def getGameStatus(self) -> int:
        return self.status

    def getWinner(self) -> int:
        return self.winner

    def resetAllPlayers(self):
        [x.resetPlayer() for x in self.players]

        with open(self.aliasFilename, "r") as f:
            randomaliases = f.readlines()
            for playerobj in self.players:

                alias = random.choice(randomaliases).strip()
                aliases = [x.getAlias() for x in self.players]

                while alias in aliases:
                    alias = random.choice(randomaliases).strip()

                playerobj.setAlias(alias)

def printGameInstance(gi: GameInstance, printResult=True) -> str:
    result = []

    result.append(f"Game Code: {gi.gamecode}")
    result.append(f"Status: {gi.status}")
    result.append(f"Winner: {gi.winner}")
    result.append(f"maxHackers: {gi.maxHackers}")
    result.append(f"maxWhitehats: {gi.maxWhitehats}")
    result.append(f"maxInvestigators: {gi.maxInvestigators}")

    result.append(f"\nPlayers: {len(gi.players)}")

    for playerobj in gi.players:
        result.append(f"Name: {playerobj.getName()}\n"
            f"Alias: {playerobj.getAlias()}\n"
            f"Role: {playerobj.getRole()}\n"
            f"Status: {playerobj.getStatus()}\n"
            f"isHacked: {playerobj.isHacked}\n"
            f"isVoted: {playerobj.isVoted}\n")

    result = "\n".join(result)
    if printResult:
        print(result)

    return result