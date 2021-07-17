var socket = io()

socket.on("reloadPage", function(data){
    alert(data);
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