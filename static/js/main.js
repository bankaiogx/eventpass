const ticketInputs = document.querySelectorAll(".ticket-quantity");
const bookingTotal = document.getElementById("booking-total");
const selectedTicketCount = document.getElementById("selected-ticket-count");
const checkoutButton = document.getElementById("checkout-button");

function updateBookingTotal() {
    let total = 0;
    let ticketCount = 0;

    ticketInputs.forEach(function (input) {
        const quantity = Number(input.value) || 0;
        const price = Number(input.dataset.price) || 0;
        ticketCount += quantity;
        total += quantity * price;
    });

    if (bookingTotal) {
        bookingTotal.textContent = total.toFixed(2);
    }

    if (selectedTicketCount) {
        if (ticketCount === 0) {
            selectedTicketCount.textContent = "No tickets selected";
        } else {
            selectedTicketCount.textContent = ticketCount === 1 ? "1 ticket selected" : ticketCount + " tickets selected";
        }
    }

    if (checkoutButton) {
        checkoutButton.disabled = ticketCount === 0;
    }
}

ticketInputs.forEach(function (input) {
    input.addEventListener("input", updateBookingTotal);
    input.addEventListener("change", updateBookingTotal);
    input.addEventListener("keyup", updateBookingTotal);
});

updateBookingTotal();

const quantityButtons = document.querySelectorAll(".quantity-button");

quantityButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        const input = this.parentElement.querySelector(".ticket-quantity");
        const currentValue = Number(input.value) || 0;
        const maxValue = Number(input.max) || 0;

        if (this.dataset.action === "increase" && currentValue < maxValue) {
            input.value = currentValue + 1;
        }

        if (this.dataset.action === "decrease" && currentValue > 0) {
            input.value = currentValue - 1;
        }

        updateBookingTotal();
    });
});

if (document.querySelector("dotlottie-player")) {
    const script = document.createElement("script");
    script.type = "module";
    script.src = "https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs";
    document.body.appendChild(script);
}

const navLinks = document.querySelectorAll("[data-nav]");
const currentPath = window.location.pathname;

navLinks.forEach(function (link) {
    const navType = link.dataset.nav;

    if (navType === "home" && currentPath === "/") {
        link.classList.add("active");
    }

    if (navType === "events" && currentPath.startsWith("/events/")) {
        link.classList.add("active");
    }

    if (navType === "tickets" && currentPath.startsWith("/accounts/my-tickets/")) {
        link.classList.add("active");
    }

    if (navType === "support" && currentPath.startsWith("/accounts/support/")) {
        link.classList.add("active");
    }

    if (navType === "profile" && currentPath.startsWith("/accounts/profile/")) {
        link.classList.add("active");
    }

    if (navType === "login" && currentPath.startsWith("/accounts/login/")) {
        link.classList.add("active");
    }

    if (navType === "register" && currentPath.startsWith("/accounts/register/")) {
        link.classList.add("active");
    }
});
