const img = document.querySelector(".banner-img");
const text = document.querySelector(".banner-text");

const tl = new TimelineMax();
tl.fromTo(img, 1, {height: "0%"}, {height: "100%", ease: Power2.easeInOut});

document.addEventListener("contextmenu", event => event.preventDefault());
