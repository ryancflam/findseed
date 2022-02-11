const t = new TimelineMax();
t.fromTo(document.querySelector(".banner-img"), 2, {height: "0%"}, {height: "100%", ease: Power2.easeInOut});
document.addEventListener("contextmenu", event => event.preventDefault());
