"""
Hacker - StrITwise 2021: Edge of Automation
Hacker is a web-based game that was created for the event, 
StrITwise 2021: Edge of Automation for Ngee Ann Polytechnic.
Copyright (C) 2021 Eugenio Manansala, Richard Pamintuan, Wong Chao Hao

This file is part of Hacker.

Hacker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Hacker is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Hacker.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
File: player.py
This file contains the implementation of the Player Classes

The Player class contains the player's states in a game. All of its attributes
are protected and can only be set using the setter and getter methods. It is
useful as when the attributes change, the getter/setter interface remains
untouched. 
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
        self.status = "online"

        self.isHacked = False
        self.isVoted = False

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setAlias(self, alias):
        self.alias = alias

    def getAlias(self):
        return self.alias

    def setRole(self, role):
        self.role = role

    def getRole(self):
        return self.role

    def setStatus(self, status):
        self.status = status

    def getStatus(self):
        return self.status

    def setHacked(self):
        self.isHacked = True

    def setVoted(self):
        self.isVoted = True

    def serialize(self):
        data = {}

        data["name"] = self.getName()
        data["alias"] = self.getAlias()
        data["role"] = self.getRole()
        data["status"] = self.getStatus()

        return data

GAMEMASTER_PLAYER = Player("GAMEMASTER")
GAMEMASTER_PLAYER.alias = "SYSTEM"

HACKER_PLAYER = Player("HACKER")
HACKER_PLAYER.alias = "SYSTEM"
HACKER_PLAYER.role = "hacker"

WHITEHAT_PLAYER = Player("WHITEHAT")
WHITEHAT_PLAYER.alias = "SYSTEM"
WHITEHAT_PLAYER.role = "whitehat"

INVESTIGATOR_PLAYER = Player("INVESTIGATOR")
INVESTIGATOR_PLAYER.alias = "SYSTEM"
INVESTIGATOR_PLAYER.role = "investigator"

CIVILIAN_PLAYER = Player("CIVILIAN")
CIVILIAN_PLAYER.alias = "SYSTEM"
CIVILIAN_PLAYER.role = "civilian"