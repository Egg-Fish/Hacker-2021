"""
File: player.py
This file contains the implementation of the Player and Spectator Classes

The Player class contains the player's states in a game. All of its attributes
are protected and can only be set using the setter and getter methods. It is
useful as when the attributes change, the getter/setter interface remains
untouched. 

The Spectator class is an extension of the player class with flags that will 
nullify its presence in the game. Spectators have the visibility of a civilian.
"""

class Player:
    def __init__(self, name):
        self.name = name
        self.alias = ""
        self.role = ""
        self.status = ""

        self.isHacked = False
        self.isVoted = False

    def resetPlayer(self):
        self.alias = ""
        self.role = ""
        self.status = ""

        self.isHacked = False
        self.isVoted = False

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setAlias(self, alias):
        pass

    def getAlias(self):
        pass

    def setRole(self, role):
        pass

    def getRole(self):
        pass

    def setStatus(self, status):
        pass

    def getStatus(self):
        pass

    def setHacked(self):
        self.isHacked = True

    def setVoted(self):
        self.isVoted = True