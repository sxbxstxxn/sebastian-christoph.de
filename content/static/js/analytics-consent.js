(function () {
    const banner = document.querySelector("[data-analytics-id]");

    if (!banner) {
        return;
    }

    const analyticsId = banner.getAttribute("data-analytics-id");
    const storageKey = "analytics-consent";

    function loadAnalytics() {
        if (document.querySelector("script[data-google-analytics]")) {
            return;
        }

        const script = document.createElement("script");
        script.async = true;
        script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(analyticsId);
        script.setAttribute("data-google-analytics", "true");
        document.head.appendChild(script);

        window.dataLayer = window.dataLayer || [];
        window.gtag = window.gtag || function () {
            window.dataLayer.push(arguments);
        };

        window.gtag("js", new Date());
        window.gtag("consent", "update", {
            analytics_storage: "granted"
        });
        window.gtag("config", analyticsId);
    }

    function hideBanner() {
        banner.hidden = true;
    }

    function showBanner() {
        banner.hidden = false;
    }

    const consent = window.localStorage.getItem(storageKey);

    if (consent === "granted") {
        loadAnalytics();
        return;
    }

    if (consent === "denied") {
        return;
    }

    showBanner();

    const acceptButton = banner.querySelector("[data-consent-accept]");
    const denyButton = banner.querySelector("[data-consent-deny]");

    if (acceptButton) {
        acceptButton.addEventListener("click", function () {
            window.localStorage.setItem(storageKey, "granted");
            loadAnalytics();
            hideBanner();
        });
    }

    if (denyButton) {
        denyButton.addEventListener("click", function () {
            window.localStorage.setItem(storageKey, "denied");
            hideBanner();
        });
    }
})();
