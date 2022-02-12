const t = new TimelineMax();
t.fromTo(document.querySelector(".banner-img"), 2, {height: "0%"}, {height: "100%", ease: Power2.easeInOut});
document.addEventListener("contextmenu", event => event.preventDefault());

function playWhenReady() {
    var d = new Date();
    var h = d.getHours();
    var m = d.getMinutes();
    var s = d.getSeconds();
    if (h === 4 && m === 0 && s === 0) {
        playSound("static/assets/4am.mp3");
        clearInterval(interval);
    }
}

function playSound(soundFile) {
    var audioElement = document.createElement("audio");
    audioElement.setAttribute("src", soundFile);
    audioElement.play();
}

var interval = setInterval("playWhenReady()", 1000);
