(function () {
    const form = document.getElementById("mis-ventas-filtros-form");
    if (!form) return;

    const applyBtn = form.querySelector(".aplicar-filtro");
    const trackedFilterNames = [
        "desde",
        "hasta",
        "matricula",
        "idv",
        "tipo_venta",
        "dni",
        "tipo_cliente",
        "nombre_cliente",
    ];

    const rows = Array.from(document.querySelectorAll("[data-result-row]"));
    const visibleCount = document.getElementById("results-visible-count");
    const loadMoreBtn = document.getElementById("load-more-results");
    const clearAllButtons = Array.from(document.querySelectorAll("[data-clear-all='true']"));
    const chipButtons = Array.from(document.querySelectorAll(".filter-chip"));

    const exportContainer = document.querySelector(".results-actions-row");
    const exportUrl = exportContainer ? exportContainer.dataset.exportUrl || "" : "";
    const exportExcelBtn = document.getElementById("export-excel-btn");
    const exportCsvBtn = document.getElementById("export-csv-btn");
    const exportMenuToggle = document.getElementById("export-menu-toggle");
    const exportOptionsMenu = document.getElementById("export-options-menu-mobile");
    const exportOptionButtons = Array.from(document.querySelectorAll("#export-options-menu-mobile [data-export-format]"));
    const mobileExportQuery = window.matchMedia("(max-width: 640px)");
    const selectedSalesCount = document.getElementById("selected-sales-count");
    const rowCheckboxes = Array.from(document.querySelectorAll("[data-select-venta]"));
    const selectAllSales = document.getElementById("select-all-sales");

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

    if (applyBtn) {
        syncApplyButtonState();
        form.addEventListener("input", syncApplyButtonState);
        form.addEventListener("change", syncApplyButtonState);
    }

    function getField(name) {
        return form.elements.namedItem(name);
    }

    function setFieldValue(name, value) {
        const field = getField(name);
        if (!field) return;
        field.value = value;
    }

    function submitFilters() {
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

    clearAllButtons.forEach((clearBtn) => {
        clearBtn.addEventListener("click", () => {
            window.location.assign(window.location.pathname);
        });
    });

    const pageSize =
        Number.parseInt(
            (loadMoreBtn && loadMoreBtn.dataset.pageSize) || "25",
            10
        ) || 25;

    function hiddenRows() {
        return rows.filter((row) => row.hidden);
    }

    function updateVisibleCounter() {
        if (!visibleCount) return;
        const visible = rows.length - hiddenRows().length;
        visibleCount.textContent = String(visible);
    }

    function syncLoadMoreState() {
        if (!loadMoreBtn) return;
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

    if (loadMoreBtn && rows.length) {
        loadMoreBtn.addEventListener("click", () => {
            if (loadMoreBtn.disabled) return;
            loadMoreBtn.disabled = true;
            loadMoreBtn.setAttribute("aria-busy", "true");
            loadMoreBtn.classList.add("is-loading");
            window.setTimeout(revealNextPage, 170);
        });
    }

    function setAllRowsSelection(checked) {
        rowCheckboxes.forEach((checkbox) => {
            checkbox.checked = checked;
        });
    }

    function getSelectedSaleIds() {
        return rowCheckboxes
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.value);
    }

    function syncSelectAllControls(selectedCount, totalCount) {
        const allChecked = totalCount > 0 && selectedCount === totalCount;
        const someChecked = selectedCount > 0 && selectedCount < totalCount;
        if (!selectAllSales) return;
        selectAllSales.checked = allChecked;
        selectAllSales.indeterminate = someChecked;
    }

    function syncExportButtonsState(selectedCount, totalCount) {
        const canExport = totalCount > 0 && selectedCount > 0;
        [exportExcelBtn, exportCsvBtn].forEach((btn) => {
            if (!btn) return;
            btn.disabled = !canExport;
        });
        if (exportMenuToggle) {
            exportMenuToggle.disabled = !canExport;
            if (!canExport) {
                closeExportMenu();
            }
        }
        exportOptionButtons.forEach((btn) => {
            btn.disabled = !canExport;
        });
    }

    function closeExportMenu() {
        if (exportOptionsMenu) {
            exportOptionsMenu.hidden = true;
        }
        if (exportMenuToggle) {
            exportMenuToggle.setAttribute("aria-expanded", "false");
        }
    }

    function openExportMenu() {
        if (!exportOptionsMenu || !exportMenuToggle || exportMenuToggle.disabled) return;
        exportOptionsMenu.hidden = false;
        exportMenuToggle.setAttribute("aria-expanded", "true");
    }

    function syncSelectionState() {
        const totalCount = rowCheckboxes.length;
        const selectedCount = getSelectedSaleIds().length;
        if (selectedSalesCount) {
            selectedSalesCount.textContent = `${selectedCount} seleccionadas`;
        }
        syncSelectAllControls(selectedCount, totalCount);
        syncExportButtonsState(selectedCount, totalCount);
    }

    rowCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", syncSelectionState);
    });

    if (selectAllSales) {
        selectAllSales.addEventListener("change", () => {
            setAllRowsSelection(selectAllSales.checked);
            syncSelectionState();
        });
    }

    function buildExportUrl(formato) {
        if (!exportUrl) return "";
        const url = new URL(exportUrl, window.location.origin);
        const formData = new FormData(form);
        for (const [name, value] of formData.entries()) {
            const normalized = String(value || "").trim();
            if (normalized) {
                url.searchParams.append(name, normalized);
            }
        }
        url.searchParams.set("formato", formato);

        const selectedIds = getSelectedSaleIds();
        url.searchParams.set("selected_ids", selectedIds.join(","));
        return url.toString();
    }

    function triggerExport(formato) {
        const selectedIds = getSelectedSaleIds();
        if (!selectedIds.length) {
            window.alert("Selecciona al menos una venta para exportar.");
            return;
        }
        const targetUrl = buildExportUrl(formato);
        if (!targetUrl) return;
        closeExportMenu();
        window.location.assign(targetUrl);
    }

    if (exportMenuToggle) {
        exportMenuToggle.addEventListener("click", () => {
            if (!mobileExportQuery.matches) {
                return;
            }
            const isOpen = exportOptionsMenu && !exportOptionsMenu.hidden;
            if (isOpen) {
                closeExportMenu();
            } else {
                openExportMenu();
            }
        });
    }

    if (exportExcelBtn) {
        exportExcelBtn.addEventListener("click", () => {
            triggerExport("excel");
        });
    }

    if (exportCsvBtn) {
        exportCsvBtn.addEventListener("click", () => {
            triggerExport("csv");
        });
    }

    exportOptionButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            triggerExport(btn.dataset.exportFormat || "excel");
        });
    });

    document.addEventListener("click", (event) => {
        if (!mobileExportQuery.matches) return;
        if (!exportOptionsMenu || exportOptionsMenu.hidden) return;
        const target = event.target;
        if (exportMenuToggle && exportMenuToggle.contains(target)) return;
        if (exportOptionsMenu.contains(target)) return;
        closeExportMenu();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        closeExportMenu();
    });

    const handleViewportChange = () => {
        if (!mobileExportQuery.matches) {
            closeExportMenu();
        }
    };
    if (typeof mobileExportQuery.addEventListener === "function") {
        mobileExportQuery.addEventListener("change", handleViewportChange);
    } else if (typeof mobileExportQuery.addListener === "function") {
        mobileExportQuery.addListener(handleViewportChange);
    }

    updateVisibleCounter();
    syncLoadMoreState();
    syncSelectionState();
    window.getActiveFilters = getActiveFilters;
})();
