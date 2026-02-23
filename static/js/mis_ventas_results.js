(function () {
    const form = document.getElementById("mis-ventas-filtros-form");
    if (!form) return;

    const rows = Array.from(document.querySelectorAll("[data-result-row]"));
    const visibleCount = document.getElementById("results-visible-count");
    const loadMoreBtn = document.getElementById("load-more-results");
    const clearAllBtn = document.querySelector("[data-clear-all='true']");
    const chipButtons = Array.from(document.querySelectorAll(".filter-chip"));

    function getField(name) {
        return form.elements.namedItem(name);
    }

    function setFieldValue(name, value) {
        const field = getField(name);
        if (!field) return;
        field.value = value;
    }

    function submitFilters() {
        if (typeof form.requestSubmit === "function") {
            form.requestSubmit();
            return;
        }
        form.submit();
    }

    function getActiveFilters() {
        const read = (name) => {
            const field = getField(name);
            return field ? String(field.value || "").trim() : "";
        };
        const current = {
            desde: read("desde"),
            hasta: read("hasta"),
            matricula: read("matricula"),
            idv: read("idv"),
            tipo_venta: read("tipo_venta"),
            dni: read("dni"),
            tipo_cliente: read("tipo_cliente"),
            nombre_cliente: read("nombre_cliente"),
        };
        const active = [];
        if (current.desde || current.hasta) active.push("periodo");
        if (current.matricula) active.push("matricula");
        if (current.idv) active.push("idv");
        if (current.tipo_venta) active.push("tipo_venta");
        if (current.dni) active.push("dni");
        if (current.tipo_cliente) active.push("tipo_cliente");
        if (current.nombre_cliente) active.push("nombre_cliente");
        return active;
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

    if (!rows.length || !loadMoreBtn) {
        window.getActiveFilters = getActiveFilters;
        return;
    }

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
    window.getActiveFilters = getActiveFilters;
})();
