var socket = io()

socket.emit('testSocket')

socket.on("reloadPage", function(){
    window.location.reload();
    alert("YERRRR");
});