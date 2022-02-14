const t = new TimelineMax();
const img = document.querySelector(".banner-img");
t.fromTo(img, 2, {height: "0%"}, {height: "100%", ease: Power2.easeInOut});
document.addEventListener("contextmenu", event => event.preventDefault());

function main() {
    var date = new Date();
    var h = date.getHours();
    var m = date.getMinutes();
    var s = date.getSeconds();
    if (h === 4 && m === 0 && s === 0) {
        document.getElementById("audio").play();
    }
}

const interval = 1000;
setInterval(main, interval);
