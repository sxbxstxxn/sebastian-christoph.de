document.addEventListener("DOMContentLoaded", function () {
    const lightboxLinks = Array.from(document.querySelectorAll("[data-lightbox]"));

    if (!lightboxLinks.length) {
        return;
    }

    let overlay = null;
    let image = null;
    let counter = null;
    let currentItems = [];
    let currentIndex = 0;

    function getGalleryItems(link) {
        const gallery = link.closest(".gallery-grid");
        const links = gallery ? gallery.querySelectorAll("[data-lightbox]") : [link];

        return Array.from(links).map(function (item) {
            const thumbnail = item.querySelector("img");

            return {
                href: item.href,
                alt: thumbnail ? thumbnail.alt : "",
            };
        });
    }

    function updateImage() {
        const item = currentItems[currentIndex];
        image.src = item.href;
        image.alt = item.alt;
        counter.textContent = (currentIndex + 1) + " / " + currentItems.length;
    }

    function showPrevious(event) {
        if (event) {
            event.stopPropagation();
        }

        currentIndex = (currentIndex - 1 + currentItems.length) % currentItems.length;
        updateImage();
    }

    function showNext(event) {
        if (event) {
            event.stopPropagation();
        }

        currentIndex = (currentIndex + 1) % currentItems.length;
        updateImage();
    }

    function closeLightbox() {
        if (!overlay) {
            return;
        }

        document.removeEventListener("keydown", handleKeydown);
        overlay.remove();
        overlay = null;
        image = null;
        counter = null;
        currentItems = [];
        currentIndex = 0;
    }

    function handleKeydown(event) {
        if (event.key === "Escape") {
            closeLightbox();
        } else if (event.key === "ArrowLeft") {
            showPrevious();
        } else if (event.key === "ArrowRight") {
            showNext();
        }
    }

    function createButton(className, label, text, onClick) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = className;
        button.setAttribute("aria-label", label);
        button.textContent = text;
        button.addEventListener("click", onClick);

        return button;
    }

    function openLightbox(link) {
        currentItems = getGalleryItems(link);
        currentIndex = currentItems.findIndex(function (item) {
            return item.href === link.href;
        });

        if (currentIndex < 0) {
            currentIndex = 0;
        }

        overlay = document.createElement("div");
        overlay.className = "lightbox-overlay";
        overlay.addEventListener("click", closeLightbox);

        const frame = document.createElement("div");
        frame.className = "lightbox-frame";
        frame.addEventListener("click", function (event) {
            event.stopPropagation();
        });

        image = document.createElement("img");
        image.className = "lightbox-image";

        const closeButton = createButton("lightbox-close", "Lightbox schliessen", "×", closeLightbox);
        const previousButton = createButton("lightbox-nav lightbox-prev", "Vorheriges Bild", "‹", showPrevious);
        const nextButton = createButton("lightbox-nav lightbox-next", "Naechstes Bild", "›", showNext);

        counter = document.createElement("div");
        counter.className = "lightbox-counter";

        frame.appendChild(image);
        overlay.appendChild(frame);
        overlay.appendChild(closeButton);
        if (currentItems.length > 1) {
            overlay.appendChild(previousButton);
            overlay.appendChild(nextButton);
            overlay.appendChild(counter);
        }
        document.body.appendChild(overlay);
        document.addEventListener("keydown", handleKeydown);

        updateImage();
    }

    lightboxLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            openLightbox(link);
        });
    });
});
