const placeholders = document.querySelectorAll(".youtube-placeholder");

placeholders.forEach((placeholder) => {

    // Klavye erişilebilirliği
    if (!placeholder.hasAttribute("tabindex")) {
        placeholder.setAttribute("tabindex", "0");
    }

    if (!placeholder.hasAttribute("role")) {
        placeholder.setAttribute("role", "button");
    }

    const loadVideo = () => {
        // Çift tetiklemeyi engelle
        if (placeholder.dataset.loaded === "true") {
            return;
        }

        const videoId = placeholder.dataset.videoId;

        if (!videoId) {
            return;
        }

        placeholder.dataset.loaded = "true";

        const iframe = document.createElement("iframe");

        // Mevcut responsive sınıfları koru
        iframe.className = placeholder.className;

        iframe.src =
            `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`;

        iframe.title =
            placeholder.dataset.title || "YouTube Video Player";

        iframe.referrerPolicy =
            "strict-origin-when-cross-origin";

        iframe.allow =
            "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";

        iframe.allowFullscreen = true;

        placeholder.replaceWith(iframe);
    };

    // Mouse / dokunmatik
    placeholder.addEventListener("click", loadVideo);

    // Klavye
    placeholder.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            loadVideo();
        }
    });
});