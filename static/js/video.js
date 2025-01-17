window.onload = function () {
    let players = document.getElementsByClassName("jsmpeg");
    for (let i = 0; i < players.length; i++) {
        console.log(i);
        players[i].playerInstance.volume = 0;
    }
}

function sound(id) {
    var player = document.getElementById("p" + id).playerInstance;
    var button = document.getElementById("s" + id);
    if (player.volume == 1) {
        player.volume = 0;
        button.innerText = "Включить звук";
    }
    else {
        player.volume = 1;
        button.innerText = "Выключить звук";
    }
}

function video(id) {
    var player = document.getElementById("p" + id);
    var button = document.getElementById("v" + id);
    if (player.style.display == "none") {
        player.style.display = "block";
        button.innerText = "Выключить изображение";
    }
    else {
        player.style.display = "none";
        button.innerText = "Включить изображение";
    }
}