(function () {
    const form = document.getElementById("mis-comunicaciones-filtros-form");
    if (!form) return;

    const applyBtn = form.querySelector(".aplicar-filtro");
    const trackedFilterNames = ["desde", "hasta", "marca", "tipo"];
    const rows = Array.from(document.querySelectorAll("[data-result-row]"));
    const visibleCount = document.getElementById("results-visible-count");
    const loadMoreBtn = document.getElementById("load-more-comunicaciones");
    const clearAllBtn = document.querySelector("[data-clear-all='true']");
    const chipButtons = Array.from(document.querySelectorAll(".filter-chip"));

    function readFilterValue(name) {
        const field = form.elements.namedItem(name);
        if (!field) return "";
        if (typeof field.value === "string") return field.value;
        return String(field.value || "");
    }

    const initialFilterState = trackedFilterNames.reduce((acc, name) => {
        acc[name] = readFilterValue(name);
        return acc;
    }, {});

    function hasFormChanges() {
        return trackedFilterNames.some(
            (name) => readFilterValue(name) !== initialFilterState[name]
        );
    }

    function syncApplyButtonState() {
        if (!applyBtn) return;
        applyBtn.disabled = !hasFormChanges();
    }

    function getField(name) {
        return form.elements.namedItem(name);
    }

    function setFieldValue(name, value) {
        const field = getField(name);
        if (!field) return;
        field.value = value;
        field.dispatchEvent(new Event("input", { bubbles: true }));
        field.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function submitFilters() {
        form.submit();
    }

    if (applyBtn) {
        syncApplyButtonState();
        form.addEventListener("input", syncApplyButtonState);
        form.addEventListener("change", syncApplyButtonState);
    }

    chipButtons.forEach((chip) => {
        chip.addEventListener("click", () => {
            const names = (chip.dataset.clearFields || "")
                .split(",")
                .map((name) => name.trim())
                .filter(Boolean);
            names.forEach((name) => setFieldValue(name, ""));
            submitFilters();
        });
    });

    if (clearAllBtn) {
        clearAllBtn.addEventListener("click", () => {
            window.location.assign(window.location.pathname);
        });
    }

    if (!rows.length || !loadMoreBtn) return;

    const pageSize = Number.parseInt(loadMoreBtn.dataset.pageSize || "25", 10) || 25;

    function hiddenRows() {
        return rows.filter((row) => row.hidden);
    }

    function updateVisibleCounter() {
        if (!visibleCount) return;
        const visible = rows.length - hiddenRows().length;
        visibleCount.textContent = String(visible);
    }

    function syncLoadMoreState() {
        const remaining = hiddenRows().length;
        if (remaining <= 0) {
            loadMoreBtn.hidden = true;
            return;
        }
        loadMoreBtn.hidden = false;
        loadMoreBtn.disabled = false;
        loadMoreBtn.removeAttribute("aria-busy");
        loadMoreBtn.classList.remove("is-loading");
    }

    function revealNextPage() {
        const next = hiddenRows().slice(0, pageSize);
        next.forEach((row) => {
            row.hidden = false;
        });
        updateVisibleCounter();
        syncLoadMoreState();
    }

    loadMoreBtn.addEventListener("click", () => {
        if (loadMoreBtn.disabled) return;
        loadMoreBtn.disabled = true;
        loadMoreBtn.setAttribute("aria-busy", "true");
        loadMoreBtn.classList.add("is-loading");
        window.setTimeout(revealNextPage, 170);
    });

    updateVisibleCounter();
    syncLoadMoreState();
})();
