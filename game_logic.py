import random
import time
import logging
import os

with open("random_names.txt", "r") as f:
    RANDOM_NAMES = f.readlines()
    RANDOM_NAMES = list(map(lambda x:x.strip(), RANDOM_NAMES))

GAMES = {}

GAME_STATUS = ["Waiting for game to start", "Game is running", "Game has ended"]
ROUND_STATUS = ["Nighttime: Hackers are voting", "Nighttime: White Hats are voting", "Nighttime: Investigators are voting", "Daytime: Everyone is awake"]

"""
Class GameInstance:
    This class will contain the game states of a single game played among
    5-8 players

Player States:
    name: The name of the player. Will not change once instantiated

    alias: The alias of the player. Will not change after being set by
    the GameInstance method, addPlayer().

    role: The role of the player. The four roles are
        - "hacker"
        - "whitehat"
        - "investigator"
        - "civilian"

    status: The status of the player. Will affect the chatbox. Only players
    who are alive can chat. The two states are
        - "online"
        - "hacked"

Explaining nested dictionaries:
    Imagine we have a dictionary called players, and:

    players = {
        "qingu" : {
            "name": "qingu",
            "alias": "John Doe",
            "role": "civilian",
            "status": "online"
            }

        "eugen" : {
            "name": "eugen",
            "alias": "Egg",
            "role": "hacker",
            "status": "online"
            }

        "richard" : {
            "name": "richa",
            "alias": "SkyrusPreyas",
            "role": "whitehat",
            "status": "hacked"
            }

        "chaohao" : {
            "name": "chaohao",
            "alias": "EuphoricBizkuits",
            "role": "investigator",
            "status": "online"
            }
        }

    To get richard's alias we can do:
    players["richard"]["alias"]
    
    players["richard"] returns a dictionary that looks like this:
    {
        "name": "richa",
        "alias": "SkyrusPreyas",
        "role": "whitehat",
        "status": "hacked"
    }

    and so we can access the other states using:
    players["richard"]["name"]
    players["richard"]["role"]
    players["richard"]["status"]


Attributes:
    gamecode: The gamecode of the game instance
    players: A dictionary of the player data, which is also a dictionary
    see the above explanation for more information.

    status: The current status of the game.
        0 - The game has not started
        1 - The game is running
        2 - The game has ended

    roundStatus: The current status of the round.
        0- Hackers are choosing their victims
        1 - Whitehats are choosing a person
        2 - Investigator is choosing a person
        3 - Daytime: Everyone talks

    nHackers, nWhitehats, nInvestigators:
        The maximum number of each role in the game. Depending on how many
        players there are in the room, the GM can adjust the numbers
        accordingly. Default value of all attributes are 0.

    hackers, whitehats, investigators:
        A list that contains the dictionaries of player data.
        E.g.,
        self.hackers = [
            {"name": "eugen","alias": "Egg","role": "hacker","status": "online"}
        ]

        The list is indexed using integers (E.g., self.hackers[0] is the first hacker in the list)
        Although self.hackers["eugen"] would be more clear, it is not needed for any logic.

    victims:
        A list of names of people who have been targeted by the hackers
"""

class GameInstance:
    def __init__(self, gamecode, nHackers = 1, nWhitehats = 1, nInvestigators = 1):
        self.gamecode = gamecode
        self.players = {}
        # A Dictionary, with the keys being the real names of the players

        self.status = 0
        # The current status of the game
        # 0 - The game has not started
        # 1 - The game is running
        # 2 - The game has ended

        self.roundStatus = 0
        # 0 - Hackers are choosing their victims
        # 1 - Whitehats are choosing a person
        # 2 - Investigator is choosing a person
        # 3 - Daytime: Everyone talks

        self.nHackers = nHackers
        self.nWhitehats = nWhitehats
        self.nInvestigators = nInvestigators
        # Maximum number of hackers, whitehats, and investigators

        self.hackers = []
        self.whitehats = []
        self.investigators = []
        # The list that will contain the details of the players
        # The real names do not need to be the key

        self.victims = []
        self.hasInvestigated = False
        self.nProtections = 0
    
    """
    Adds a player to the player dictionary.
    The real name is used as the key.

    Note: if a player with the same username is added, the
    player entry will be overriden.
    """
    def add_player(self, player:dict):
        player["alias"] = random.choice(RANDOM_NAMES)

        aliases = [self.players[x]["alias"] for x in self.players]

        while player["alias"] in aliases:
            player["alias"] = random.choice(RANDOM_NAMES)

        self.players.update({player["name"] : player})

        logging.info(f"User {player['name']} with alias {player['alias']} has joined the game {self.gamecode}")

    """
    Parses the game states into a single new-line-escaped string
    """
    def getGameData(self):
        result = {}
        result["gamecode"] = self.gamecode
        result["players"] = self.players
        result["status"] = self.status
        result["roundStatus"] = self.roundStatus
        result["nHackers"] = self.nHackers
        result["nWhitehats"] = self.nWhitehats
        result["nInvestigators"] = self.nInvestigators
        
        result["hackers"] = self.hackers
        result["whitehats"] = self.whitehats
        result["investigators"] = self.investigators

        result["victims"] = self.victims
        result["hasInvestigated"] = self.hasInvestigated
        result["nProtections"] = self.nProtections

        return result

    def getRoundData(self): # Player-Safe Data
        result = {}
        result["gamecode"] = self.gamecode
        result["status"] = self.status
        result["roundStatus"] = self.roundStatus

        result["victims"] = self.victims
        result["hasInvestigated"] = self.hasInvestigated
        result["nProtections"] = self.nProtections

        return result

    """
    Initialises the player roles and sets the game and round status to 1 and 0
    """
    def startGame(self):
        logging.info(f"[GC: {self.gamecode}] The game is starting")
        self.status = 1 # Game in progress
        self.roundStatus = 0 # Hackers' turn to speak
        self.hasInvestigated = False # Investigator can investigate
        self.nProtections = 0

        player_names = [p for p in self.players]
        random.shuffle(player_names) # Randomise the order of the names of players

        for p in player_names:
            player = self.players[p]

            if len(self.hackers) < self.nHackers:
                self.hackers.append(player)
                player["role"] = "hacker"
                logging.info(f"[GC: {self.gamecode}] Player {player['name']} is a Hacker")

            elif len(self.whitehats) < self.nWhitehats:
                self.whitehats.append(player)
                player["role"] = "whitehat"
                logging.info(f"[GC: {self.gamecode}] Player {player['name']} is a White Hat")

            elif len(self.investigators) < self.nInvestigators:
                self.investigators.append(player)
                player["role"] = "investigator"
                logging.info(f"[GC: {self.gamecode}] Player {player['name']} is a Investigator")

            else:
                player["role"] = "civilian"
                logging.info(f"[GC: {self.gamecode}] Player {player['name']} is a Cilivian")


    def startHackers(self):
        self.roundStatus = 0 # Hackers' turn to speak
        self.victims.clear()


    def startWhitehats(self):
        self.roundStatus = 1 # White Hats' turn to speak
        self.nProtections = 0 # Number of protects that the whitehats gave


    def startInvestigators(self):
        self.roundStatus = 2 # Investigators' turn to speak
        self.hasInvestigated = False # Investigator can investigate

    def startCivilians(self):
        self.roundStatus = 3 # Hackers' turn to speak

    # Removes duplicate names in the list, self.victims.
    def removeDuplicateVictims(self):
        pass

    # Adds a player with alias, alias into the list, self.victims. 
    # Return -1 if alias is not in the game.
    # Return 0 on successful execution.
    def hackVictim(self, alias):
        pass

    # Removes a player with alias, alias from the list, self.victims. 
    # Return -1 if alias is not in the game. 
    # Return -2 if the whitehats have exhausted their 
    # protection limit (aka the number of whitehats). 
    # Return -3 if the victims list is empty.
    # Return 0 and add 1 to self.nProtections on successful execution.
    def protectPlayer(self, alias):
        pass

    # Returns the role of a player whose alias is alias. Set the hasInvestigated 
    # flag to True if investigation is successful. 
    # Return -1 if alias is not in the game. 
    # Return -2 if the investigator has already investigated. 
    # Return the role of the player on successful execution.
    def investigateAlias(self, alias):
        return "SUSSY BAKA"


    # Picks a final victim in self.victims
    # Returns the name of the final victim
    # Returns 0 if self.victims is empty (The white hats 
    # have successfully protected the civilians)
    def endNight(self):
        if len(self.victims) == 0:
            return 0
        else:
            finalVictim = random.choice(self.victims)

            return finalVictim

    



def create_player(name):
    player = \
    {
        "name" :        name,
        "alias" :       "",
        "role" :        "",
        "status" :      "online",
    }

    return player



"""
Parameters:
    name: the name of the player
    gamecode: the current gamecode that the player is in

Returns:
    True (boolean) if the role is allowed to chat in the chatbox
    at that point in time, else False (boolean)
"""
def isAllowedToSpeak(name, gamecode):
    game = GAMES[gamecode] # This returns the GameInstance object of the current game
    # Tip:
    # game.players["richard"]["alias"] returns "SkyrusPreyas"
    # likewise game.players[name]["alias"] returns the alias of the player whos name is name.
    pass