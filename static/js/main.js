const cards = document.querySelectorAll(".event-card");

cards.forEach(function (card) {
    card.addEventListener("mouseenter", function () {
        this.style.transform = "scale(1.03)";
    });

    card.addEventListener("mouseleave", function () {
        this.style.transform = "scale(1)";
    });
});

const ticketInputs = document.querySelectorAll(".ticket-quantity");
const bookingTotal = document.getElementById("booking-total");

function updateBookingTotal() {
    let total = 0;

    ticketInputs.forEach(function (input) {
        const quantity = Number(input.value) || 0;
        const price = Number(input.dataset.price) || 0;
        total += quantity * price;
    });

    if (bookingTotal) {
        bookingTotal.textContent = total.toFixed(2);
    }
}

ticketInputs.forEach(function (input) {
    input.addEventListener("input", updateBookingTotal);
    input.addEventListener("change", updateBookingTotal);
    input.addEventListener("keyup", updateBookingTotal);
});

updateBookingTotal();

if (document.querySelector("dotlottie-player")) {
    const script = document.createElement("script");
    script.type = "module";
    script.src = "https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs";
    document.body.appendChild(script);
}
