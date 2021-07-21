var socket = io()

socket.on("reloadPage", function(data){
    window.location.reload();
});

function inWaitingRoom() {
    setTimeout(function () {
        socket.emit("command", "inWaitingRoom");
        inWaitingRoom();
    }, 1000);
}

socket.on("waitingRoomData", function(data){
    var players = document.getElementsByClassName("players")[0];
    players.innerHTML = "";

    for (playerName in data){
        const d = document.createElement("div");
        d.className = "player";

        d.innerHTML = "<span>" + data[playerName] + "</span>";

        players.appendChild(d);
    }
});

function inGamemasterRoom() {
    setTimeout(function () {
        socket.emit("command", "inGamemasterRoom");
        inGamemasterRoom();
    }, 1000);
}

socket.on("gamemasterRoomData", function(data){
    var players = document.getElementsByClassName("players")[0];
    players.innerHTML = "";

    for (player in data["players"]){
        const d = document.createElement("div");
        d.className = "player";

        playerName = data["players"][player]["name"];
        playerAlias = data["players"][player]["alias"];
        playerRole = data["players"][player]["role"];
        playerStatus = data["players"][player]["status"];

        d.innerHTML = "<span>" + 
            "Name: "+ playerName + "<br>" +
            "Alias: "+ playerAlias + "<br>" +
            "Role: "+ playerRole + "<br>" +
            "Status: "+ playerStatus + "</span>";

        players.appendChild(d);
    }
});

function startGame(){
    socket.emit("command", "startGame");
}


function inGameRoom() {
    setTimeout(function () {
        socket.emit("command", "inGameRoom");
        inGameRoom();
    }, 1000);
}

socket.on("gameRoomData", function(data){
    console.log(data);
    var playerInfo = document.getElementsByClassName("playerInfo")[0];

    playerName = data["playerInfo"]["name"];
    playerAlias = data["playerInfo"]["alias"];
    playerRole = data["playerInfo"]["role"];
    playerStatus = data["playerInfo"]["status"];

    playerInfo.innerHTML = "<img src='/static/usericon.png'>" + 
    "<span>" +
    "Name:" + playerName + "<br>" +
    "Alias:" + playerAlias + "<br>" +
    "Role:" + playerRole + "<br>" +
    "Status:" + playerStatus + "<br>" +
    "</span>";

    var output = document.getElementById("output");
    output.innerHTML = "";
    
    for (messageNo in data["messages"]){
        message = data["messages"][messageNo];
        output.innerHTML += message;
    }
});


function sendMessage(message){
    socket.emit("message", message);
}