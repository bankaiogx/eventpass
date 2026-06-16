const cards = document.querySelectorAll(".event-card");

cards.forEach(function (card) {
    card.addEventListener("mouseenter", function () {
        this.style.transform = "scale(1.03)";
    });

    card.addEventListener("mouseleave", function () {
        this.style.transform = "scale(1)";
    });
});
