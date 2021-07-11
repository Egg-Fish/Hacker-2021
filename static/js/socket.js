var socket = io()

function getGameData(){
    socket.emit("getGameData");
}

socket.on("gameData", function(data){
    var d = document.getElementById("output");
    d.innerHTML = data;
});

function startGame(){
    alert("Starting game for all participants...");
    socket.emit("startGame");
}

socket.on('startGame', function(){
    alert("the game is starting...");
    window.location = "/";
});

socket.on("playerData", function(data){
    var name = data["name"];
    var alias = data["alias"];
    var role = data["role"];
    var status = data["status"];

    var nameElement = document.getElementById("playerName");
    var aliasElement = document.getElementById("playerAlias");
    var roleElement = document.getElementById("playerRole");
    var statusElement = document.getElementById("playerStatus");

    nameElement.innerHTML = name;
    aliasElement.innerHTML = alias;
    roleElement.innerHTML = role;
    statusElement.innerHTML = status;
})

function messagePlayers(){
    var message = document.getElementById("message").value;
    document.getElementById("message").value = "";
    socket.emit("alertRoom", {"message": message, "room": "player"})
}

function messageHackers(){
    var message = document.getElementById("message").value;
    document.getElementById("message").value = "";
    socket.emit("alertRoom", {"message": message, "room": "hacker"})
}

function messageWhitehats(){
    var message = document.getElementById("message").value;
    document.getElementById("message").value = "";
    socket.emit("alertRoom", {"message": message, "room": "whitehat"})
}

function messageInvestigators(){
    var message = document.getElementById("message").value;
    document.getElementById("message").value = "";
    socket.emit("alertRoom", {"message": message, "room": "investigator"});
}

socket.on("alertMessage", function(msg){
    var message = msg["message"];
    alert(message);
});

function sendMessage(){
    var message = document.getElementById("message").value;
    document.getElementById("message").value = "";
    socket.emit("sendMessage", {"message": message});
}

socket.on("message", function(data){
    var sender = data["sender"];
    var message = data["message"];

    document.getElementById("output").innerHTML += sender + ": " + message + "\n";
});