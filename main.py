import random
import time
import logging
import os

from flask import Flask, send_file, send_from_directory
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask import render_template, request, redirect, session

from game_logic import GameInstance, create_player, GAMES

NIGHT_START_MESSAGE_ALL = {"sender": "SYSTEM", "message": "The night has started. The hacker(s) is choosing their victims."}
NIGHT_START_MESSAGE_HACKERS = {"sender": "SYSTEM", "message": "You are a Hacker. Do /t <alias> to target a victim. Type /c to end your turn."}
NIGHT_START_MESSAGE_WHITEHATS = {"sender": "SYSTEM", "message": "You are a White Hat. Do /p <alias> to protect a person from being hacked. Can only be used once per round per white hat. Type /c to end your turn."}
NIGHT_START_MESSAGE_INVESTIGATOR = {"sender": "SYSTEM", "message": "You are the one and only Invesigator. Do /s <alias> to reveal the role of a person. Can only be used once per round. Type /c to end your turn."}

NIGHT_END_HACKERS_MESSAGE_ALL = {"sender": "SYSTEM", "message": "The hackers have chosen their victims."}
NIGHT_END_WHITEHATS_MESSAGE_ALL = {"sender": "SYSTEM", "message": "The white hats have chosen who to protect."}
NIGHT_END_INVESTIGATOR_MESSAGE_ALL = {"sender": "SYSTEM", "message": "The investigator has revealed the role of a person."}

DAY_START_MESSAGE_ALL = {"sender": "SYSTEM", "message": "The night has ended. Everyone wakes up."}
DAY_VOTE_MESSAGE_ALL = {"sender": "SYSTEM", "message": "You can now vote for who you think is(are) the hacker(s) using /vote <alias>. Type /c if you wish to skip voting."}


logging.basicConfig(
    filename="logs\log.log",
    filemode="w+", 
    level=logging.DEBUG, 
    format='[%(asctime)s][%(funcName)s][%(levelname)s]:%(message)s')

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
socketio = SocketIO(app, async_mode="eventlet")

# SocketIO Library
@app.route("/socket/socket.io.js")
def sendSocketIOFile():
    return send_file("socket/socket.io.js")
    


# TEST: REMOVE IN PRODUCTION
oriontestgame = GameInstance("oriontestgame")
GAMES.update({"oriontestgame": oriontestgame})

dummygame = GameInstance("dummygame", nWhitehats=2, nHackers=2)

dummyplayer1 = create_player("dummy1")
dummygame.add_player(dummyplayer1)

dummyplayer2 = create_player("dummy2")
dummygame.add_player(dummyplayer2)

dummyplayer3 = create_player("dummy3")
dummygame.add_player(dummyplayer3)

dummyplayer4 = create_player("dummy4")
dummygame.add_player(dummyplayer4)

dummyplayer5 = create_player("dummy5")
dummygame.add_player(dummyplayer5)

dummyplayer6 = create_player("dummy6")
dummygame.add_player(dummyplayer6)

dummyplayer7 = create_player("dummy7")
dummygame.add_player(dummyplayer7)

dummyplayer8 = create_player("dummy8")
dummygame.add_player(dummyplayer8)

dummygame.startGame()
dummygame.startHackers()

GAMES.update({"dummygame": dummygame})

@app.route("/test/<path>")
def test(path):
    session["name"] = "dummy1"
    session["gamecode"] = "dummygame"
    session["role"] = "hacker"
    session["alias"] = "sussybaka"

    if path == "endscreen.html":
        dummygame.winner = random.randint(1,2)
    
    return render_template(path)

# Application Events
@app.route("/", methods=["POST", "GET"])
def game():
    host = request.host

    if request.method == "POST":
        name = request.form['name']
        gamecode = request.form['gamecode']

        if len(name.strip()) == 0 or len(gamecode.strip()) == 0:
            return render_template("joinscreen.html")

        else:
            session["name"] = name
            session["gamecode"] = gamecode

            player = create_player(name)
            game = GAMES[gamecode]
            game.add_player(player)

            return render_template("waitingscreen.html")

    else:
        if "gamecode" in session and "name" in session:
            game = GAMES[session["gamecode"]]
            if game.status == 0:
                return render_template("waitingscreen.html")

            if game.status == 1:
                return render_template("game.html")

            elif game.status == 2:
                return render_template("endscreen.html")
        
        else:
            return render_template("joinscreen.html")

# GM Screen
@app.route("/create_game")
def createGame():
    gamecode = str(random.randint(10000000, 99999999))

    game = GameInstance(gamecode)
    GAMES.update({gamecode: game})
    session["gm"] = True
    session["gamecode"] = gamecode

    return redirect(f"/gm")



@app.route("/gm")
def gamemaster():
    if "gm" in session and session["gm"] and session["gamecode"]:
        return render_template("gmscreen.html")
    else:
        return "YOU ARE NOT THE GM"

@app.route("/gm/<gamecode>")
def oriontestgame(gamecode):
    session["gm"] = True
    session["gamecode"] = gamecode
    return render_template("gmscreen.html")



# Debug Screen
@app.route("/debug/<gamecode>")
def debug(gamecode):
    session["gamecode"] = gamecode
    logging.debug(f"Debugger has joined {gamecode}")
    return render_template("debug.html")

@socketio.on("startGame")
def startGame():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    game.startGame() # Initialises everything for the game to start

    emit("startGame", to=f"{gamecode}/player") # Sends a message to the players to refresh the page

@socketio.on("getGameData")
def getGameData():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    data = game.getGameData()

    emit("gameData", data)

@socketio.on("getGameData_gm")
def getGameData():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    data = game.getGameData()

    emit("gameData_gm", data)



@socketio.on("alertRoom")
def alertRoom(data):
    message = data["message"]
    room = data["room"]

    gamecode = session["gamecode"]
    gameroom = gamecode + "/" + room

    logging.debug(f"Sending alertMessage to {gameroom} (message: {message})")
    emit("alertMessage", {"message": message}, to=gameroom)


@socketio.on("startHackers")
def startHackers():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    emit("clearChat", to=f"{gamecode}/player")
    emit("message", NIGHT_START_MESSAGE_ALL, to=f"{gamecode}/player")
    emit("message", NIGHT_START_MESSAGE_HACKERS, to=f"{gamecode}/hacker")
    emit("message", {
        "sender": "SYSTEM", 
        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
    }, to=f"{gamecode}/hacker")

    game.startHackers()

@socketio.on("startWhitehats")
def startWhitehats():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    emit("clearChat", to=f"{gamecode}/player")
    emit("message", NIGHT_END_HACKERS_MESSAGE_ALL, to=f"{gamecode}/player")
    emit("message", NIGHT_START_MESSAGE_WHITEHATS, to=f"{gamecode}/whitehat")
    emit("message", {
        "sender": "SYSTEM", 
        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
    }, to=f"{gamecode}/whitehat")

    game.startWhitehats()

@socketio.on("startInvestigators")
def startInvestigators():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    emit("clearChat", to=f"{gamecode}/player")
    emit("message", NIGHT_END_WHITEHATS_MESSAGE_ALL, to=f"{gamecode}/player")
    emit("message", NIGHT_START_MESSAGE_INVESTIGATOR, to=f"{gamecode}/investigator")
    emit("message", {
        "sender": "SYSTEM", 
        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
    }, to=f"{gamecode}/investigator")

    game.startInvestigators()

@socketio.on("startCivilians")
def startCivilians():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    emit("clearChat", to=f"{gamecode}/player")
    emit("message", NIGHT_END_INVESTIGATOR_MESSAGE_ALL, to=f"{gamecode}/player")
    emit("message", {
        "sender": "SYSTEM", 
        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
    }, to=f"{gamecode}/player")

    game.startCivilians()

@socketio.on("clearChat")
def clearChat():
    gamecode = session["gamecode"]
    emit("clearChat", to=f"{gamecode}/player")


# SocketIO Events
@socketio.on("connect")
def connect():
    host = request.host
    logging.debug(f"Host {host} has connected")

@socketio.on("disconnect")
def disconnect():
    host = request.host
    logging.debug(f"Host {host} has disconnected")

@socketio.on("joinGameRoom")
def joinGameRoom():
    gamecode = session["gamecode"]
    name = session['name']

    game = GAMES[gamecode]
    role = GAMES[gamecode].players[name]["role"]

    session["role"] = role

    join_room(gamecode + "/player")
    logging.debug(f"User {session['name']} has joined the socket room [{gamecode}/player]")

    if "role" in session:
        join_room(gamecode + "/" + role)
        logging.debug(f"User {session['name']} has joined the socket room [{gamecode}/{role}]")

    emit("newPlayer", game.players, to=f"{gamecode}/player")


@socketio.on("getPlayerData")
def getPlayerData():
    name = session["name"]
    gamecode = session["gamecode"]

    player = GAMES[gamecode].players[name]

    emit("playerData", player)

@socketio.on("getRoundData")
def getRoundData():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    data = game.getRoundData()

    emit("roundData", data)

# Helper command
def isAuthorised(player_role, round_status):
    return True

def createOnlineAliasesString(l):
    result = ["Current Online Players:"]

    for alias in l:
        result.append(alias)

    return "\n".join(result)

@socketio.on("sendMessage")
def sendMessage(data):
    gamecode = session["gamecode"]
    name = session["name"]

    game = GAMES[gamecode]
    player = GAMES[gamecode].players[name]

    
    role = player["role"]

    sender = player["alias"]
    message = data["message"]

    logging.debug(f"[GC: {gamecode}] Message received from {name}: {message}")

    if player["status"] != "online": # Player is out of the game
        message = "You are offline. Better luck next time."
        emit("message", {"sender": "SYSTEM", "message": message})
        return

    else: # Player is in turn
        if not message or len(message) > 500:
            return
        
        if message[0] == "/": # Is a command
            logging.debug(f"Command {message} received from {name} ({role})")
            m = message.split(maxsplit=1)
            command = m[0]

            if (command == "/continue" or command == "/c")\
            and (\
                (player["role"] == "hacker" and game.roundStatus == 0)\
                or (player["role"] == "whitehat" and game.roundStatus == 1)\
                or (player["role"] == "investigator" and game.roundStatus == 2)\
                or (game.roundStatus == 3)
            ):
                game.continuers[name] = 1
                rs = game.continueGame()

                emit("message", {"sender": "SYSTEM", "message": f"Waiting for other players to continue..."})

                roundStatus = rs[0]

                if roundStatus == -1:
                    return

                if roundStatus == 0:
                    emit("clearChat", to=f"{gamecode}/player")
                    if game.finalVote and game.finalRole:
                        emit("message", {
                            "sender": "SYSTEM", 
                            "message": f"The player {game.finalVote} has been voted out. The player was a {game.finalRole}"
                        }, to=f"{gamecode}/player")
                    else:
                        emit("message", {
                            "sender": "SYSTEM", 
                            "message": "Noone was voted out."
                        }, to=f"{gamecode}/player")

                    emit("message", NIGHT_START_MESSAGE_ALL, to=f"{gamecode}/player")
                    emit("message", NIGHT_START_MESSAGE_HACKERS, to=f"{gamecode}/hacker")
                    emit("message", {
                        "sender": "SYSTEM", 
                        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
                    }, to=f"{gamecode}/hacker")

                elif roundStatus == 1:
                    emit("clearChat", to=f"{gamecode}/player")
                    emit("message", NIGHT_END_HACKERS_MESSAGE_ALL, to=f"{gamecode}/player")
                    emit("message", NIGHT_START_MESSAGE_WHITEHATS, to=f"{gamecode}/whitehat")
                    emit("message", {
                        "sender": "SYSTEM", 
                        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
                    }, to=f"{gamecode}/whitehat")


                elif roundStatus == 2:
                    emit("clearChat", to=f"{gamecode}/player")
                    emit("message", NIGHT_END_WHITEHATS_MESSAGE_ALL, to=f"{gamecode}/player")
                    emit("message", NIGHT_START_MESSAGE_INVESTIGATOR, to=f"{gamecode}/investigator")
                    emit("message", {
                        "sender": "SYSTEM", 
                        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
                    }, to=f"{gamecode}/investigator")

                elif roundStatus == 3:
                    if game.nOffline > 0:
                        if game.nOnlineHackers == 0:
                            game.winner = 2
                            game.status = 2
                            emit("endGame", to=f"{gamecode}/player")
                            return

                        elif game.nOnline - game.nOnlineHackers <= game.nOnlineHackers:
                            game.winner = 1
                            game.status = 2
                            emit("endGame", to=f"{gamecode}/player")
                            return

                    emit("clearChat", to=f"{gamecode}/player")
                    # emit("message", NIGHT_END_INVESTIGATOR_MESSAGE_ALL, to=f"{gamecode}/player")
                    emit("message", DAY_START_MESSAGE_ALL, to=f"{gamecode}/player")
                    if game.finalVictim:
                        emit("message", {"sender": "SYSTEM", "message": f"The player {game.finalVictim} has been hacked! This player can no longer communicate."}, to=f"{gamecode}/player")
                    else:
                        emit("message", {"sender": "SYSTEM", "message": f"Nobody has been hacked!"}, to=f"{gamecode}/player")

                    emit("message", DAY_VOTE_MESSAGE_ALL, to=f"{gamecode}/player")
                    emit("message", {
                        "sender": "SYSTEM", 
                        "message": createOnlineAliasesString(game.getOnlinePlayerAliases())
                    }, to=f"{gamecode}/player")

                elif roundStatus > 3: # Game win scenario
                    emit("endGame", to=f"{gamecode}/player")

                return

            if len(m) < 2 and (command != "/continue" and command != "/c"):
                emit("message", {"sender": "SYSTEM", "message": "INVALID COMMAND"})
                return

            if (command == "/target" or command == "/t") and player["role"] == "hacker" and game.roundStatus == 0:
                result = game.hackVictim(m[1])
                if result == -1:
                    emit("message", {"sender": "SYSTEM", "message": f"Alias {m[1]} is not in the game"})
                elif result == 0:
                    emit("message", {"sender": "SYSTEM", "message": f"Alias {m[1]} has been targeted"}, to=f"{gamecode}/hacker")
                
                logging.debug(f"Command game.hackVictim with parameter {m[1]} returned {result}")

            elif (command == "/protect" or command == "/p") and player["role"] == "whitehat" and game.roundStatus == 1:
                result = game.protectPlayer(m[1])

                if result == -1:
                    emit("message", {"sender": "SYSTEM", "message": f"Alias {m[1]} is not in the game"})
                elif result == -2:
                    emit("message", {"sender": "SYSTEM", "message": f"Your team has already used this ability {game.nProtections} time(s)"}, to=f"{gamecode}/whitehat")
                else:
                    emit("message", {"sender": "SYSTEM", "message": f"Protecting {m[1]}..."}, to=f"{gamecode}/whitehat")
                
                logging.debug(f"Command game.protectPlayer with parameter {m[1]} returned {result}")

            elif (command == "/scan" or command == "/s") and player["role"] == "investigator" and game.roundStatus == 2:
                result = game.investigateAlias(m[1])
                if result == -1:
                    emit("message", {"sender": "SYSTEM", "message": f"Alias {m[1]} is not in the game"})
                elif result == -2:
                    emit("message", {"sender": "SYSTEM", "message": f"You have already used this ability"})
                elif result:
                    emit("message", {"sender": "SYSTEM", "message": f"The alias {m[1]} is a {result}"}, to=f"{gamecode}/investigator")
                
                logging.debug(f"Command game.investigateAlias with parameter {m[1]} returned {result}")

            elif command == "/vote" and game.roundStatus == 3:
                result = game.votePlayer(m[1])
                if result == -1:
                    emit("message", {"sender": "SYSTEM", "message": f"Alias {m[1]} is not in the game"})
                elif result == 0:
                    emit("message", {"sender": "SYSTEM", "message": f"{player['name']} has voted for {m[1]}"}, to=f"{gamecode}/player")
                elif result == 1:
                    emit("message", {"sender": "SYSTEM", "message": f"All players have voted. Type /c to continue."}, to=f"{gamecode}/player")

                

                

            elif (command == "/target" or command == "/t") \
            or (command == "/protect" or command == "/p") \
            or (command == "/scan" or command == "/s") \
            or (command == "/vote") \
            or (command == "/continue" or command == "/c"):
                emit("message", {"sender": "SYSTEM", "message": f"You cannot use this command at this point in time"})

            else:
                logging.debug(f"Command Not Found")
                emit("message", {"sender": "SYSTEM", "message": f"COMMAND NOT FOUND"})

            return

        if game.roundStatus < 3:
            sender = "Anonymous"
            gameroom = gamecode + "/" + role

        else:
            gameroom = gamecode + "/player"

        logging.debug(f"[GC: {gamecode}] Sending message to {gameroom}")
        emit("message", {"sender": sender, "message": message}, to=gameroom)

@socketio.on("getEndGameData")
def getEndGameData():
    gamecode = session["gamecode"]

    game = GAMES[gamecode]

    data = game.getEndGameData()

    emit("endGameData", data)


if __name__ == "__main__":
    socketio.run(
        app=app, 
        host="0.0.0.0", 
        port="80", 
        debug=True)