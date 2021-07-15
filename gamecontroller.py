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

        self.victims = []
        self.protected = []
        self.scanned = []

        self.votes = {}
        self.continues = {}

        self.messages = []
        self.hackerMessages = []
        self.whitehatMessages = []
        self.investigatorMessages = []
        self.civilianMessages = []

    def addPlayer(self, playerobj:Player):
        self.gameinstance.players.append(playerobj)
        pass

    def removePlayer(self, playerName:str):
        playerobj = self.gameinstance.getPlayerFromName(playerName)
        if playerobj:
            self.gameinstance.players.remove(playerobj)
        pass

    def handleMessage(self, playerName, data) -> int:
        # JS emits sent with the "message" event are handled here
        # Returns -1 if there was an error
        pass

    def handleCommand(self, playerName, data) -> int:
        # JS emits sent with the "command" event are handled here
        # Returns -1 if command is not found
        pass

    def authorMessage(self, playerobj:Player) -> str:
        fs = "{}@{}: "
        return fs.format(playerobj.getAlias(), self.gamecode)

    def addMessage(self, playerobj, message):
        message = self.authorMessage(playerobj) + message
        self.messages.append(message)

    def addMessageToRole(self, playerobj:Player, message):
        # Uses the role found in playerobj
        message = self.authorMessage(playerobj) + message
        playerRole = playerobj.getRole()

        if playerRole == "hacker":
            self.hackerMessages.append(message)
        elif playerRole == "whitehat":
            self.whitehatMessages.append(message)
        elif playerRole == "investigator":
            self.investigatorMessages.append(message)
        elif playerRole == "civilian":
            self.civilianMessages.append(message)
        else:
            self.messages.append(message)

    def getMessages(self) -> List[str]:
        return self.messages

    def getMessagesForRole(self, role) -> List[str]:
        if role == "hacker":
            return self.hackerMessages
        elif role == "whitehat":
            return self.whitehatMessages
        elif role == "investigator":
            return self.investigatorMessages
        elif role == "civilian":
            return self.civilianMessages
        else:
            return self.messages

    def isAllowedToSpeak(self, playerobj:Player) -> bool:
        playerRole = playerobj.getRole()

    def clearMessages(self, role="") -> None:
        pass



    def targetAlias(self, playerobj:Player, alias) -> int:
        pass

    def protectAlias(self, playerobj:Player, alias) -> int:
        pass

    def scanAlias(self, playerobj:Player, alias) -> int:
        pass

    def voteAlias(self, playerobj:Player, alias) -> int:
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

def printGameController(gc: GameController, printResult=True):
    result = []

    result.append(f"Game Code: {gc.gamecode}")
    
    result.append(f"\nVictims:")
    for playerobj in gc.victims:
        result.append(f"Name: {playerobj.name}\n"
            f"Alias: {playerobj.alias}\n"
            f"Role: {playerobj.role}\n"
            f"Status: {playerobj.status}\n"
            f"isHacked: {playerobj.isHacked}\n"
            f"isVoted: {playerobj.isVoted}\n")

    result.append(f"\nProtected:")
    for playerobj in gc.protected:
        result.append(f"Name: {playerobj.name}\n"
            f"Alias: {playerobj.alias}\n"
            f"Role: {playerobj.role}\n"
            f"Status: {playerobj.status}\n"
            f"isHacked: {playerobj.isHacked}\n"
            f"isVoted: {playerobj.isVoted}\n")

    result.append(f"\nScanned:")
    for playerobj in gc.scanned:
        result.append(f"Name: {playerobj.name}\n"
            f"Alias: {playerobj.alias}\n"
            f"Role: {playerobj.role}\n"
            f"Status: {playerobj.status}\n"
            f"isHacked: {playerobj.isHacked}\n"
            f"isVoted: {playerobj.isVoted}\n")

    result.append(f"\nVotes:")
    for voter in gc.votes:
        result.append(f"Voter: {voter}\n"
            f"Votee: {gc.votes[voter]}\n")

    result.append(f"\nContinues:")
    for continuer in gc.continues:
        result.append(f"Continuer: {continuer}\n"
            f"Value: {gc.continues[continuer]}\n")

    result.append("\nPublic Messages:")
    for message in gc.messages:
        result.append(message)

    result.append("\nHacker Messages:")
    for message in gc.hackerMessages:
        result.append(message)

    result.append("\nWhite Hat Messages:")
    for message in gc.whitehatMessages:
        result.append(message)

    result.append("\nInvestigator Messages:")
    for message in gc.investigatorMessages:
        result.append(message)

    result.append("\nCivilian Messages:")
    for message in gc.civilianMessages:
        result.append(message)

    result = "\n".join(result)
    if printResult:
        print(result)

    return result