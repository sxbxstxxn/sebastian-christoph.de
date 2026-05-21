document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-lightbox]").forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();

            const overlay = document.createElement("div");
            overlay.className = "lightbox-overlay";

            const image = document.createElement("img");
            image.src = link.href;

            overlay.appendChild(image);
            document.body.appendChild(overlay);

            overlay.addEventListener("click", function () {
                overlay.remove();
            });
        });
    });
});