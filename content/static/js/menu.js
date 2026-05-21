document.addEventListener("DOMContentLoaded", function () {
    const button = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".main-nav");

    if (!button || !nav) return;

    button.addEventListener("click", function () {
        nav.classList.toggle("is-open");
    });
});