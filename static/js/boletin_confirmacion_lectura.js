(function () {
    const modal = document.getElementById("boletinConfirmModal");
    if (!modal) return;

    const openButtons = Array.from(document.querySelectorAll(".js-boletin-open"));
    const closeButtons = Array.from(modal.querySelectorAll("[data-modal-close]"));
    const confirmButton = document.getElementById("boletinConfirmAccept");
    const nameNode = document.getElementById("boletinConfirmName");
    let selectedUrl = "";
    let lastFocused = null;

    function setOpenState(isOpen) {
        modal.classList.toggle("is-open", isOpen);
        modal.setAttribute("aria-hidden", isOpen ? "false" : "true");
        document.body.classList.toggle("boletin-modal-open", isOpen);
        if (isOpen) {
            confirmButton.focus();
        } else if (lastFocused && typeof lastFocused.focus === "function") {
            lastFocused.focus();
        }
    }

    function openModal(url, boletinName, sourceElement) {
        selectedUrl = url || "";
        lastFocused = sourceElement || null;
        if (nameNode) {
            nameNode.textContent = boletinName || "seleccionado";
        }
        setOpenState(true);
    }

    function closeModal() {
        selectedUrl = "";
        setOpenState(false);
    }

    openButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            const href = button.getAttribute("href");
            const boletinName = button.dataset.boletinTitulo || "seleccionado";
            openModal(href, boletinName, button);
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeModal);
    });

    modal.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && modal.classList.contains("is-open")) {
            closeModal();
        }
    });

    if (confirmButton) {
        confirmButton.addEventListener("click", () => {
            const urlToOpen = selectedUrl;
            if (!urlToOpen) return;
            const target = new URL(urlToOpen, window.location.origin);
            target.searchParams.set("registrar_lectura", "1");
            setOpenState(false);
            window.setTimeout(() => {
                window.location.assign(target.toString());
            }, 60);
        });
    }
})();
