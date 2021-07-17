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