var socket = io()

socket.emit('testSocket')

socket.on("reloadPage", function(data){
    alert(data);
});