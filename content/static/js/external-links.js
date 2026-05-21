document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll("a[href]").forEach(function (link) {

        const href = link.getAttribute("href");

        if (!href) return;

        const isExternal =
            href.startsWith("http://") ||
            href.startsWith("https://");

        const isOwnDomain =
            href.includes("localhost:8000") ||
            href.includes("sebastian-christoph.de");

        if (isExternal && !isOwnDomain) {
            link.setAttribute("target", "_blank");
            link.setAttribute("rel", "noopener noreferrer");
        }
    });

});