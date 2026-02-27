(function () {
    const layout = document.querySelector(".mis-ventas-page .main-layout");
    const toggleBtn = document.querySelector(".mis-ventas-page .filters-toggle");
    const panel = document.getElementById("filtersPanel");
    const backdrop = document.querySelector(".mis-ventas-page .filters-backdrop");
    const form = document.getElementById("mis-ventas-filtros-form");
    const closeButtons = Array.from(panel ? panel.querySelectorAll("[data-filters-close]") : []);
    if (!layout || !toggleBtn || !panel) return;
    const countNode = toggleBtn.querySelector("[data-filters-count]");

    const STORAGE_KEY = "misVentasFiltersCollapsed";
    const mobileQuery = window.matchMedia("(max-width: 600px)");
    const sheetQuery = window.matchMedia("(max-width: 600px)");
    const shortLandscapeDialogQuery = window.matchMedia(
        "(max-width: 600px) and (orientation: landscape) and (max-height: 500px)"
    );

    function isFocusTrapMode() {
        return sheetQuery.matches || shortLandscapeDialogQuery.matches;
    }
    function getFocusableElements() {
        return Array.from(
            panel.querySelectorAll(
                "a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex='-1'])"
            )
        ).filter((el) => !el.hasAttribute("hidden") && el.offsetParent !== null);
    }

    function readFilterValue(name) {
        if (!form) return "";
        const field = form.elements.namedItem(name);
        if (!field) return "";
        return String(field.value || "").trim();
    }

    function getActiveFilterCount() {
        if (!form) {
            return document.querySelectorAll(".active-filters .filter-chip").length;
        }
        let count = 0;
        const desde = readFilterValue("desde");
        const hasta = readFilterValue("hasta");
        if (desde || hasta) count += 1;
        if (readFilterValue("matricula")) count += 1;
        if (readFilterValue("idv")) count += 1;
        if (readFilterValue("tipo_venta")) count += 1;
        if (readFilterValue("dni")) count += 1;
        if (readFilterValue("tipo_cliente")) count += 1;
        if (readFilterValue("nombre_cliente")) count += 1;
        return count;
    }

    function syncToggleCount() {
        const count = getActiveFilterCount();
        if (countNode) {
            countNode.textContent = String(count);
            countNode.hidden = count === 0;
        }
        const label = count > 0 ? `Filtros (${count})` : "Filtros";
        toggleBtn.setAttribute("aria-label", label);
        const labelNode = toggleBtn.querySelector(".filters-toggle__label");
        if (labelNode) {
            labelNode.textContent = "Filtros";
        }
    }

    function getStoredCollapsed() {
        try {
            const value = window.localStorage.getItem(STORAGE_KEY);
            if (value === "1" || value === "0") return value === "1";
        } catch (error) {
            return null;
        }
        return null;
    }

    function saveCollapsed(collapsed) {
        try {
            window.localStorage.setItem(STORAGE_KEY, collapsed ? "1" : "0");
        } catch (error) {
            // Ignore storage failures (private mode / restricted storage)
        }
    }

    function focusFirstFilterField() {
        const firstField = panel.querySelector("input, select, textarea, button");
        if (firstField && typeof firstField.focus === "function") {
            firstField.focus();
            return;
        }
        if (typeof panel.focus === "function") {
            panel.focus();
        }
    }

    function setCollapsed(collapsed, options) {
        const opts = options || {};
        const persist = opts.persist !== false;
        const focusOnOpen = opts.focusOnOpen === true;
        const isMobile = mobileQuery.matches;

        if (isMobile) {
            layout.classList.remove("filters-collapsed");
            layout.classList.toggle("filters-open", !collapsed);
            if (backdrop) backdrop.classList.toggle("is-visible", !collapsed);
            document.body.classList.toggle("filters-drawer-open", !collapsed);
            toggleBtn.setAttribute("aria-expanded", String(!collapsed));
            if (!collapsed && focusOnOpen) {
                focusFirstFilterField();
            }
        } else {
            layout.classList.remove("filters-open");
            layout.classList.toggle("filters-collapsed", collapsed);
            if (backdrop) backdrop.classList.remove("is-visible");
            document.body.classList.remove("filters-drawer-open");
            toggleBtn.setAttribute("aria-expanded", String(!collapsed));
        }

        if (persist) saveCollapsed(collapsed);
        syncToggleCount();
    }

    function isCollapsed() {
        if (mobileQuery.matches) {
            return !layout.classList.contains("filters-open");
        }
        return layout.classList.contains("filters-collapsed");
    }

    function initializeState() {
        const stored = getStoredCollapsed();
        const initialCollapsed = stored !== null ? stored : mobileQuery.matches;
        setCollapsed(initialCollapsed, { persist: false });
    }

    toggleBtn.addEventListener("click", () => {
        const nextCollapsed = !isCollapsed();
        setCollapsed(nextCollapsed, {
            persist: true,
            focusOnOpen: mobileQuery.matches && !nextCollapsed,
        });
    });

    closeButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            setCollapsed(true, { persist: true });
            toggleBtn.focus();
        });
    });

    if (backdrop) {
        backdrop.addEventListener("click", () => {
            setCollapsed(true, { persist: true });
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            if (!mobileQuery.matches) return;
            if (!layout.classList.contains("filters-open")) return;
            setCollapsed(true, { persist: true });
            toggleBtn.focus();
            return;
        }

        if (event.key !== "Tab") return;
        if (!isFocusTrapMode()) return;
        if (!layout.classList.contains("filters-open")) return;
        const focusable = getFocusableElements();
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = document.activeElement;
        if (event.shiftKey && active === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && active === last) {
            event.preventDefault();
            first.focus();
        }
    });

    const handleViewportChange = () => {
        const stored = getStoredCollapsed();
        const collapsed = stored !== null ? stored : mobileQuery.matches;
        setCollapsed(collapsed, { persist: false });
    };

    if (typeof mobileQuery.addEventListener === "function") {
        mobileQuery.addEventListener("change", handleViewportChange);
    } else if (typeof mobileQuery.addListener === "function") {
        mobileQuery.addListener(handleViewportChange);
    }

    if (form) {
        form.addEventListener("input", syncToggleCount);
        form.addEventListener("change", syncToggleCount);
        form.addEventListener("submit", () => {
            setCollapsed(true, { persist: true });
        });
    }

    initializeState();
    syncToggleCount();
})();
