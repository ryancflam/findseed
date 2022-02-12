const t = new TimelineMax();
const img = document.querySelector(".banner-img");
t.fromTo(img, 2, {height: "0%"}, {height: "100%", ease: Power2.easeInOut});
document.addEventListener("contextmenu", event => event.preventDefault());

function play4AM() {
    var date = new Date();
    var h = date.getHours();
    var m = date.getMinutes();
    var s = date.getSeconds();
    if (h === 4 && m === 3 && s === 0) {
        document.getElementById("audio").play();
    }
}

const interval = 1000;
setInterval("play4AM()", interval);
