const cards = document.querySelectorAll(".event-card");

cards.addEventListener("mouseenter", function () {
    this.style.transform = "scale(1.03)";
});

cards.addEventListener("mouseleave", function () {
    this.style.transform = "scale(1)";
});
