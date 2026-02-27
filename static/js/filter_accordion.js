(function () {
    const accordions = Array.from(document.querySelectorAll(".filters .filter-accordion"));
    if (!accordions.length) return;
    const mobileSheetQuery = window.matchMedia("(max-width: 600px)");
    const shortLandscapeDialogQuery = window.matchMedia(
        "(max-width: 600px) and (orientation: landscape) and (max-height: 500px)"
    );

    const isSingleOpenMode = () =>
        mobileSheetQuery.matches || shortLandscapeDialogQuery.matches;

    const setOpen = (accordion, open, immediate) => {
        const header = accordion.querySelector(".filter-accordion__header");
        const content = accordion.querySelector(".filter-accordion__content");
        if (!header || !content) return;

        header.setAttribute("aria-expanded", open ? "true" : "false");
        accordion.classList.toggle("is-open", open);

        if (open) {
            if (immediate) {
                content.style.transition = "none";
                content.style.maxHeight = "none";
                requestAnimationFrame(() => {
                    content.style.transition = "";
                });
            } else {
                const height = content.scrollHeight;
                content.style.maxHeight = height + "px";
            }
            return;
        }

        if (content.style.maxHeight === "none") {
            content.style.maxHeight = content.scrollHeight + "px";
            requestAnimationFrame(() => {
                content.style.maxHeight = "0px";
            });
        } else {
            content.style.maxHeight = "0px";
        }
    };

    accordions.forEach((accordion) => {
        const header = accordion.querySelector(".filter-accordion__header");
        const content = accordion.querySelector(".filter-accordion__content");
        if (!header || !content) return;

        const startsOpen =
            accordion.classList.contains("is-open") ||
            header.getAttribute("aria-expanded") === "true";
        setOpen(accordion, startsOpen, true);

        header.addEventListener("click", () => {
            const isOpen = accordion.classList.contains("is-open");
            const willOpen = !isOpen;
            if (willOpen && isSingleOpenMode()) {
                accordions.forEach((otherAccordion) => {
                    if (otherAccordion === accordion) return;
                    if (!otherAccordion.classList.contains("is-open")) return;
                    setOpen(otherAccordion, false, false);
                });
            }
            setOpen(accordion, willOpen, false);
        });

        content.addEventListener("transitionend", (event) => {
            if (event.propertyName !== "max-height") return;
            if (!accordion.classList.contains("is-open")) return;
            content.style.maxHeight = "none";
        });
    });

    window.addEventListener("resize", () => {
        accordions.forEach((accordion) => {
            if (!accordion.classList.contains("is-open")) return;
            const content = accordion.querySelector(".filter-accordion__content");
            if (!content) return;
            if (content.style.maxHeight === "none") return;
            content.style.maxHeight = content.scrollHeight + "px";
        });
    });
})();
