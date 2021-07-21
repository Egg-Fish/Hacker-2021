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

// sleep time expects milliseconds
function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
  }
  
// // Usage!
// sleep(500).then(() => {
//     // Do something after the sleep!
// });

prevGameStatus = false;

socket.on("gameRoomData", function(data){
    console.log(data);
    var playerInfo = document.getElementsByClassName("playerInfo")[0];

    playerName = data["playerInfo"]["name"];
    playerAlias = data["playerInfo"]["alias"];
    playerRole = data["playerInfo"]["role"];
    playerStatus = data["playerInfo"]["status"];

    currentGameStatus = data["status"];

    playerInfo.innerHTML = "<img src='/static/usericon.png'>" + 
    "<span>" +
    "Name:" + playerName + "<br>" +
    "Alias:" + playerAlias + "<br>" +
    "Role:" + playerRole + "<br>" +
    "Status:" + playerStatus + "<br>" +
    "</span>";

    if (currentGameStatus != prevGameStatus){
        // transition html to black
        document.getElementsByTagName("body")[0].className = "blacked";
        setTimeout(() => document.getElementsByTagName("body")[0].className = "", 2000);
        setTimeout(function(){
            var output = document.getElementById("output");
            output.innerHTML = "";
            
            for (messageNo in data["messages"]){
                message = data["messages"][messageNo];
                output.innerHTML += message;
            }
            
            var video = document.getElementById('background');
            if (currentGameStatus != prevGameStatus){
                if(currentGameStatus == true){ // day
                    document.getElementById('background').innerHTML = '<source src="/static/day.m4v" type="video/mp4">'
                    video.load();
                    video.play();
                }
                else{
                    document.getElementById('background').innerHTML = '<source src="/static/night.m4v" type="video/mp4">'
                    video.load();
                    video.play();
                }
    
                prevGameStatus = data["status"];
            }
        }, 1000);
        
    }

    else{
        var output = document.getElementById("output");
        output.innerHTML = "";
        
        for (messageNo in data["messages"]){
            message = data["messages"][messageNo];
            output.innerHTML += message;
        }
    }
});


function sendMessage(message){
    socket.emit("message", message);
}