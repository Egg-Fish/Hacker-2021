"""
File: player.py
This file contains the implementation of the GameController Class.

The GameController class is the most important class of the whole game. It
contains all the interactions between the GameInstance, the SocketController,
and the Flask application itself. It has the ability to invoke any methods of
the three (except for socket communication).
"""
from typing import List, Set, Dict, Tuple, Optional

from gameinstance import GameInstance
from socketcontroller import SocketController

from player import Player
"""
Implementation Notes:
Communication at night:
    Each player is assigned to a socket room called <gamecode>/<role>
    and a room called <gamecode>.
    
    At night, only the <gamecode>/<role> rooms are used for comms. The main
    room is left alone.

    During the day, only the <gamecode> room is used for comms. The other 3
    rooms are left alone.


"""
class GameController:
    def __init__(self, gamecode:str, gameinstance:GameInstance, SocketController:SocketController):
        self.gamecode = gamecode
        self.gameinstance = gameinstance
        self.socketcontroller : SocketController

        self.victims = {}
        self.protected = {}
        self.scanned = {}

        self.votes = {}
        self.continues = {}

        self.messages = []
        self.hackerMessages = []
        self.whitehatMessages = []
        self.investigatorMessages = []
        self.civilianMessages = []

    def addPlayer(self, playerobj:Player):
        pass

    def removePlayer(self, playerName:str):
        pass

    def handleMessage(self, playerName, data) -> int:
        # JS emits sent with the "message" event are handled here
        # Returns -1 if there was an error
        pass

    def handleCommand(self, playerName, data) -> int:
        # JS emits sent with the "command" event are handled here
        # Returns -1 if command is not found
        pass

    def addMessage(self, playerobj, message):
        pass

    def addMessageToRole(self, playerobj, message):
        # Uses the role found in playerobj
        pass

    def getMessages(self) -> List[str]:
        # ADMIN COMMAND
        pass

    def getMessagesForRole(self, role) -> List[str]:
        pass

    def isAllowedToSpeak(self, playerobj) -> bool:
        pass

    def clearMessages(self, role="") -> None:
        pass



    def targetAlias(self, playerobj, alias) -> int:
        pass

    def protectAlias(self, playerobj, alias) -> int:
        pass

    def scanAlias(self, playerobj, alias) -> int:
        pass

    def voteAlias(self, playerobj, alias) -> int:
        pass

    def hasEveryoneVoted(self) -> bool:
        # Note - Do not count offline H/WH/I/C
        pass

    def hasEveryoneContinued(self) -> bool:
        # Note - Do not count offline H/WH/I/C
        # Note - A use of a command will update the continue state also

        pass


    def startNight(self) -> None:
        pass

    def endNight(self) -> str:
        pass

    def startDay(self) -> None:
        pass

    def endDay(self) -> str:
        pass

