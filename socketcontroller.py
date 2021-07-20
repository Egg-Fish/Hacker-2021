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
This file contains the implementation of the SocketController Class

The SocketController class handles outbound connections for the GameController.
The inbound traffic is handled by the main SocketIO application, just that the
contents of the traffic is handled by 
    GameController.handleCommand() and
    GameController.handleMessage()

The SocketController has a few ways of delivering outbound traffic:
    1. Rooms
    These are the <gamecode>/<role> rooms that have been used in version 0.1.
    This is used during the night to send out the specialised messages for the
    roles, as well as for anonymous communication during the night.
    
    2. Client SIDs
    The player's name is tied directly to the client's SID. Delivering a specific
    message to a player through the player's name is now possible. In the event
    that method 1 fails, we can loop through the names of the players and sent it
    directly to their clients. The rooms are named <gamecode>/<SID>

    3. Spectators
    Spectators have the visibility of a civilian, but they are not part of the game.
    They will be in the <gamecode> room and that room only. They can only see
    messages during the day.
"""
from typing import List, Set, Dict, Tuple, Optional
import logging
import time

from flask import Flask, request, session, render_template, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

class SocketController:
    def __init__(self, gamecode:str, socketio:SocketIO):
        self.gamecode = gamecode
        self.socketio = socketio
        self.clients = {} # dict[name: sid]

    def addClientToController(self, name:str, SID:str):
        # Add client entry as dict[<name>: <gamecode>/<SID>]
        self.clients.update({name: f"{self.gamecode}/{SID}"})
        logging.debug(f"User {name} has been added to the SocketController under {self.gamecode}/{SID}.")

    def sendMessagesToRoom(self, messages:List[str], room:str = "") -> None:
        # Defaults to sending to <gamecode> (a.k.a Players + Spectators)
        pass

    def sendMessagesToClient(self, messages:List[str], name:str) -> None:
        # Sends to room <gamecode>/<SID>
        pass

    def sendDataToRoom(self, data, room:str = "", event:str="data") -> None:
        # Defaults to sending to <gamecode> (a.k.a Players + Spectators)
        socketRoom = self.gamecode + "/" + room

        if not room:
            socketRoom = self.gamecode

        logging.debug(f"Sending data {data} of type {type(data)} under event {event} to room {room} under the socket room {socketRoom}.")
        self.socketio.emit(event, data, to=socketRoom)

    def sendDataToClient(self, data, name:str, event:str="data") -> None:
        # Sends to room <gamecode>/<SID>
        socketRoom = self.clients[name]

        logging.debug(f"Sending data {data} of type {type(data)} under event {event} to client {name} under the socket room {socketRoom}.")
        self.socketio.emit(event, data, to=socketRoom)