"""
File: player.py
This file contains the implementation of the GameController Class.

The GameController class is the most important class of the whole game. It
contains all the interactions between the GameInstance, the SocketController,
and the Flask application itself. It has the ability to invoke any methods of
the three (except for socket communication).
"""
from typing import List, Set, Dict, Tuple, Optional
from collections import Counter
import os, sys
import logging
import time
import math
import random

from gameinstance import GameInstance
from socketcontroller import SocketController

from player import Player, GAMEMASTER_PLAYER, HACKER_PLAYER, WHITEHAT_PLAYER, INVESTIGATOR_PLAYER, CIVILIAN_PLAYER
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
    def __init__(self, gamecode:str, gameinstance:GameInstance, socketcontroller:SocketController):
        self.gamecode = gamecode
        self.gameinstance = gameinstance
        self.socketcontroller = socketcontroller

        self.victims = []
        self.protected = []
        self.scanned = []

        self.finalVictim = None

        self.votes = {}
        self.continues = {}

        self.messages = []
        self.hackerMessages = []
        self.whitehatMessages = []
        self.investigatorMessages = []
        self.civilianMessages = []

        self.isDay = False

    def startGame(self) -> None:
        # Players are not at game.html yet
        self.gameinstance.setGameStatus(1)
        self.victims = []
        self.protected = []
        self.scanned = []

        self.gameinstance.hackers.clear()
        self.gameinstance.whitehats.clear()
        self.gameinstance.investigators.clear()
        self.gameinstance.civilians.clear()
        self.gameinstance.spectators.clear()

        self.finalVictim = None

        self.votes = {}
        self.continues = {}

        self.messages = []
        self.hackerMessages = []
        self.whitehatMessages = []
        self.investigatorMessages = []
        self.civilianMessages = []

        self.isDay = False

        self.gameinstance.resetAllPlayers()

        random.shuffle(self.gameinstance.players)

        for playerobj in self.gameinstance.players:
            if len(self.gameinstance.hackers) != self.gameinstance.maxHackers:
                playerobj.setRole("hacker")
                self.gameinstance.hackers.append(playerobj)

            elif len(self.gameinstance.whitehats) != self.gameinstance.maxWhitehats:
                playerobj.setRole("whitehat")
                self.gameinstance.whitehats.append(playerobj)

            elif len(self.gameinstance.investigators) != self.gameinstance.maxInvestigators:
                playerobj.setRole("investigator")
                self.gameinstance.investigators.append(playerobj)

            else:
                playerobj.setRole("civilian")
                self.gameinstance.civilians.append(playerobj)

        # Add predefined messages here

        # self.addMessageToAll(GAMEMASTER_PLAYER, "Welcome to Hacker 2021 by StrITwise!")

        self.startNight()

        # Send reloadPage event to players. Game has started

        self.socketcontroller.sendDataToRoom("gameStart", event="reloadPage")

    def endGame(self) -> None:
        # Ask all players to refresh
        # Winner wouldve been set before this call
        self.gameinstance.setGameStatus(2)
        self.isDay = True
        self.addMessage(CIVILIAN_PLAYER, "Scanning all players...")

        self.socketcontroller.sendDataToRoom("gameEnd", event="reloadPage")


        

    def addPlayer(self, playerobj:Player):
        self.gameinstance.players.append(playerobj)
        logging.info(f"Added player {playerobj.getName()} to game {self.gamecode}")

    def removePlayer(self, playerName:str):
        playerobj = self.gameinstance.getPlayerFromName(playerName)
        if playerobj:
            self.gameinstance.players.remove(playerobj)
            logging.info(f"Removed player {playerName} to game {self.gamecode}")

    def handleMessage(self, playerName, data) -> int:
        # JS emits sent with the "message" event are handled here
        # Returns -1 if there was an error
        # The GAMEMASTER user will go through the command event handler
        playerobj = self.gameinstance.getPlayerFromName(playerName)
        message = data

        if not playerobj:
            logging.warning(f"Player {playerName} not found in game {self.gamecode}")
            return -1

        if self.isAllowedToSpeak(playerobj) and message[0] != '/':
            if self.isDay:
                self.addMessage(playerobj, message)
            else:
                self.addMessageToRole(playerobj, message)

            for player in self.gameinstance.getPlayers():
                self.handleCommand(player.getName(), "inGameRoom")

        elif self.isAllowedToSpeak(playerobj) and message[0] == '/':
            command, number = message.strip().split(maxsplit=1)
            if command in ["/v", "/vote"] and self.isDay:
                self.voteAlias(playerobj, number)
                

            if command in ["/t", "/target"]:
                self.targetAlias(playerobj, number)
                

            if command in ["/p", "/protect"]:
                self.protectAlias(playerobj, number)
                

            if command in ["/s", "/scan"]:
                self.scanAlias(playerobj, number)
                
            self.updateGame()
        pass

    def handleCommand(self, playerName, data) -> int:
        # JS emits sent with the "command" event are handled here
        # Returns -1 if command is not found
        playerobj = self.gameinstance.getPlayerFromName(playerName)
        command = data.strip()

        if not playerobj and playerName != "GAMEMASTER":
            logging.warning(f"Player {playerName} not found in game {self.gamecode}")
            return -1

        if command == "inWaitingRoom":
            data = []

            for player in self.gameinstance.getPlayers():
                data.append(player.getName())

            self.socketcontroller.sendDataToClient(data, playerName, "waitingRoomData")
            return

        if command == "inGameRoom":
            data = {
                "playerInfo": [],
                "messages": []
            }

            data["playerInfo"] = playerobj.serialize()
            
            if self.isDay:
                data["messages"] = self.getMessages()
            else:
                data["messages"] = self.getMessagesForRole(playerobj.getRole())

            self.socketcontroller.sendDataToClient(data, playerName, "gameRoomData")
            return

        if command == "inEndgameRoom":
            return

        if playerName == "GAMEMASTER":
            # Admin commands
            if command == "inGamemasterRoom":
                data = {"players": [], "status": self.gameinstance.getGameStatus()}

                for player in self.gameinstance.getPlayers():
                    data["players"].append(player.serialize())

                self.socketcontroller.sendDataToClient(data, playerName, "gamemasterRoomData")
                return

            if command == "startGame":
                self.startGame()
                return
            
            if command == "endGame":
                self.endGame()
                return

            if command.split(":")[0].strip() == "sendMessage":
                # command = "sendMessage:Hello World!"
                self.addMessageToAll(GAMEMASTER_PLAYER, command.split(":")[1].strip())
                return
        
        pass

    def authorMessage(self, playerobj:Player) -> str:
        fs = "<b>{}@{}: </b>"
        if playerobj.getName() == "GAMEMASTER":
            return fs.format("GAMEMASTER", self.gamecode)
        if self.isDay:
            return fs.format(playerobj.getAlias(), self.gamecode)
        else:
            return fs.format("Anonymous", self.gamecode)

    def addMessage(self, playerobj, message):
        message = self.authorMessage(playerobj) + message + "<br>"
        logging.debug(f"Message [{message}] added.")
        self.messages.append(message)

    def addMessageToRole(self, playerobj:Player, message):
        # Uses the role found in playerobj
        message = self.authorMessage(playerobj) + message + "<br>"
        playerRole = playerobj.getRole()

        logging.debug(f"Message [{message}] added to {playerRole} chat.")
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

    def addMessageToAll(self, playerobj:Player, message):
        # GAMEMASTER COMMAND
        message = self.authorMessage(playerobj) + message + "<br>"

        self.hackerMessages.append(message)
        self.whitehatMessages.append(message)
        self.investigatorMessages.append(message)
        self.civilianMessages.append(message)
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

        if playerRole == "spectator":
            logging.debug(f"Player with role {playerRole} is not allowed to speak. (isDay = {self.isDay})")
            return False

        if playerobj.getStatus() != "online":
            logging.debug(f"Player with role {playerRole} is not allowed to speak. (isDay = {self.isDay})")
            return False

        if self.isDay:
            return True

        if playerRole == "civilian" and self.isDay:
            return True

        if playerRole in ["hacker", "whitehat", "investigator"] and not self.isDay:
            return True

        logging.debug(f"Player with role {playerRole} is not allowed to speak. (isDay = {self.isDay})") 
        return False

    def clearMessages(self, role="") -> None:
        if role:
            if role == "hacker":
                return self.hackerMessages.clear()
            elif role == "whitehat":
                return self.whitehatMessages.clear()
            elif role == "investigator":
                return self.investigatorMessages.clear()
            elif role == "civilian":
                return self.civilianMessages.clear()
        else:
            self.messages.clear()
            self.hackerMessages.clear()
            self.whitehatMessages.clear()
            self.investigatorMessages.clear()
            self.civilianMessages.clear()

    def showOnlinePlayers(self):
        # Sends a list of online aliases
        message = []
        players = self.gameinstance.getOnlinePlayers()

        message.append("<br>Current Online Members:")
        for i in range(len(players)):
            message.append(f"<i>{i+1}: {players[i].getAlias()}</i>")

        msg = "<br>".join(message)

        self.addMessageToAll(GAMEMASTER_PLAYER, msg)



    def targetAlias(self, playerobj:Player, number:str) -> int:
        # Note - Number is derived from the position of the
        # result of self.gameinstance.getOnlinePlayers()
        if not playerobj or not number.isdigit():
            return -1

        if playerobj.getRole() != "hacker":
            return -1
        
        players = self.gameinstance.getOnlinePlayers()
        # raise Exception(players)
        index = int(number)
        
        if len(self.victims) == len(self.gameinstance.getOnlinePlayersFromRole("hacker")):
            # Can no longer target
            self.addMessageToRole(HACKER_PLAYER, f"The hackers have already chosen {len(self.victims)} victim(s) to target.")
            return -1
        
        if index == 0:
            self.continues[playerobj.getName()] = 1
            self.addMessageToRole(HACKER_PLAYER, "A hacker has chosen to target nobody.")
            return 0

        if index >= (len(players) + 1) or index < 0: # Illegal number
            self.addMessageToRole(HACKER_PLAYER, f"Invalid number {index} chosen by a hacker.")
            return -1

        else:
            self.victims.append(players[index - 1])
            self.continues[playerobj.getName()] = 1
            self.addMessageToRole(HACKER_PLAYER, f"The player {players[index - 1].getAlias()} has been targeted.")
            
            return 0


    def protectAlias(self, playerobj:Player, number:str) -> int:
        # Note - Number is derived from the position of the
        # result of self.gameinstance.getOnlinePlayers()
        if not playerobj or not number.isdigit():
            return -1

        if playerobj.getRole() != "whitehat":
            return -1
        
        players = self.gameinstance.getOnlinePlayers()
        # raise Exception(players)
        index = int(number)
        
        if len(self.protected) == len(self.gameinstance.getOnlinePlayersFromRole("whitehat")):
            # Can no longer target
            self.addMessageToRole(WHITEHAT_PLAYER, f"The white hats have already chosen {len(self.protected)} player(s) to protect.")
            return -1
        
        if index == 0:
            self.continues[playerobj.getName()] = 1
            self.addMessageToRole(WHITEHAT_PLAYER, "A white hat has chosen to protect nobody.")
            return 0

        if index >= (len(players) + 1) or index < 0: # Illegal number
            self.addMessageToRole(WHITEHAT_PLAYER, f"Invalid number {index} chosen by a white hat.")
            return -1

        else:
            self.protected.append(players[index - 1])
            self.continues[playerobj.getName()] = 1
            self.addMessageToRole(WHITEHAT_PLAYER, f"The player {players[index - 1].getAlias()} has been protected.")
            
            return 0

    def scanAlias(self, playerobj:Player, number:str) -> int:
        # Note - Number is derived from the position of the
        # result of self.gameinstance.getOnlinePlayers()
        if not playerobj or not number.isdigit():
            return -1

        if playerobj.getRole() != "investigator":
            return -1
        
        players = self.gameinstance.getOnlinePlayers()
        # raise Exception(players)
        index = int(number)
        
        if len(self.scanned) == len(self.gameinstance.getOnlinePlayersFromRole("investigator")):
            # Can no longer target
            self.addMessageToRole(INVESTIGATOR_PLAYER, f"The investigators have already chosen {len(self.scanned)} player(s) to scan.")
            return -1
        
        if index == 0:
            self.continues[playerobj.getName()] = 1
            self.addMessageToRole(INVESTIGATOR_PLAYER, "An investigator has chosen to scan nobody.")
            return 0

        if index >= (len(players) + 1) or index < 0: # Illegal number
            self.addMessageToRole(INVESTIGATOR_PLAYER, f"Invalid number {index} chosen by an investigator.")
            return -1

        else:
            self.scanned.append(players[index - 1])
            self.continues[playerobj.getName()] = 1
            self.addMessageToRole(INVESTIGATOR_PLAYER, f"The player {players[index - 1].getAlias()} is a {players[index - 1].getRole()}.")
            
            return 0

    def voteAlias(self, playerobj:Player, number:str) -> int:
        # Note - Number is derived from the position of the
        # result of self.gameinstance.getOnlinePlayers()
        if not playerobj or not number.isdigit():
            return -1
        
        players = self.gameinstance.getOnlinePlayers()
        # raise Exception(players)
        index = int(number)
        
        if index == 0:
            self.continues[playerobj.getName()] = 1
            self.addMessage(CIVILIAN_PLAYER, f"{playerobj.getAlias()} has chosen not to vote for anyone.")
            return 0

        if index >= (len(players) + 1) or index < 0: # Illegal number
            self.addMessage(CIVILIAN_PLAYER, f"Invalid number {index} chosen by {playerobj.getAlias()}.")
            return -1

        else:
            self.votes.update({playerobj.getAlias(): players[index - 1]})
            self.continues[playerobj.getName()] = 1
            self.addMessage(CIVILIAN_PLAYER, f"The player {playerobj.getAlias()} has voted for {players[index - 1].getAlias()}.")
            
            return 0

    def hasEveryoneVoted(self) -> bool:
        # Note - Do not count offline H/WH/I/C
        nOnlinePlayers = len(self.gameinstance.getOnlinePlayers())

        if len(self.votes) == nOnlinePlayers:
            return True
        else:
            return False

    def hasEveryoneContinued(self) -> bool:
        # Note - Do not count offline H/WH/I/C
        # Note - A use of a command will update the continue state also
        nOnlinePlayers = len(self.gameinstance.getOnlinePlayers())
        nOnlineCivilians = len(self.gameinstance.getOnlinePlayersFromRole("civilian"))

        if self.isDay:
            if nOnlinePlayers == len(self.continues):
                return True
        
        else:
            if nOnlinePlayers - nOnlineCivilians == len(self.continues):
                return True

        return False


    def startNight(self) -> None:
        self.victims = []
        self.protected = []
        self.scanned = []

        self.finalVictim = None

        self.votes = {}
        self.continues = {}

        self.clearMessages()

        self.isDay = False

        self.addMessageToAll(GAMEMASTER_PLAYER, "The night has started. Good luck ppl!")
        self.showOnlinePlayers()


    def endNight(self) -> str:
        # Note - Will implement the messaging
        self.clearMessages()
        self.finalVictim = None

        if len(self.victims) == 0:
            return

        self.finalVictim = random.choice(self.victims)

        if len(self.protected) == 0:
            # Hacked
            self.finalVictim.setStatus("hacked")
            return

        random.shuffle(self.protected)
        if self.finalVictim == self.protected[0]:
            # Protected
            self.finalVictim = None
            return
        else:
            # Hacked
            self.finalVictim.setStatus("hacked")
            return


    def startDay(self) -> None:
        self.isDay = True

        if self.finalVictim == None:
            # Protected
            self.addMessage(CIVILIAN_PLAYER, "Nobody was hacked.")
            
        else:
            # Hacked
            self.addMessage(CIVILIAN_PLAYER, f"The player {self.finalVictim.getAlias()} has been hacked. The player can no longer communicate.")
            
        self.showOnlinePlayers()

        self.votes = {}
        self.continues = {}


    def endDay(self) -> str:
        # Note - Will implement the messaging
        self.clearMessages()

        if len(self.votes) == 0:
            self.addMessage(CIVILIAN_PLAYER, f"Noone has been voted out.")
            return

        votes = Counter(self.votes.values())
        finalVoteAlias = votes.most_common(1)[0][0].getAlias()

        playerobj = self.gameinstance.getPlayerFromAlias(finalVoteAlias)

        self.addMessage(CIVILIAN_PLAYER, f"The player {finalVoteAlias} has been voted out. The player was a {playerobj.getRole()}")

        playerobj.setStatus("voted out")


    def updateGame(self):
        if self.hasEveryoneContinued() and not self.isDay:
            self.endNight()
            self.startDay()

        elif (self.hasEveryoneContinued() or self.hasEveryoneVoted()) \
        and self.isDay:
            self.endDay()
            self.startNight()

        # Check for win

        nHackers = len(self.gameinstance.getOnlinePlayersFromRole("hacker"))
        nOnline = len(self.gameinstance.getOnlinePlayers())
        if nHackers == 0:
            # Players win
            self.gameinstance.winner = 2
            self.endGame()
            return

        if nOnline - nHackers <= nHackers: 
            # If there are 2 online hackers, they win if 4 people are left.
            self.gameinstance.winner = 1
            self.endGame()


            

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