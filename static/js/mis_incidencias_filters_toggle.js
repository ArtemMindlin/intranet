(function () {
    const layout = document.querySelector(".mis-incidencias-page .main-layout");
    const toggleBtn = document.querySelector(".mis-incidencias-page .filters-toggle");
    const panel = document.getElementById("filtersPanel");
    const backdrop = document.querySelector(".mis-incidencias-page .filters-backdrop");
    if (!layout || !toggleBtn || !panel) return;

    const STORAGE_KEY = "misIncidenciasFiltersCollapsed";
    const mobileQuery = window.matchMedia("(max-width: 1024px)");

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
            // Ignore storage failures.
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
            if (!collapsed && focusOnOpen) focusFirstFilterField();
        } else {
            layout.classList.remove("filters-open");
            layout.classList.toggle("filters-collapsed", collapsed);
            if (backdrop) backdrop.classList.remove("is-visible");
            document.body.classList.remove("filters-drawer-open");
            toggleBtn.setAttribute("aria-expanded", String(!collapsed));
        }

        if (persist) saveCollapsed(collapsed);
    }

    function isCollapsed() {
        if (mobileQuery.matches) return !layout.classList.contains("filters-open");
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

    if (backdrop) {
        backdrop.addEventListener("click", () => {
            setCollapsed(true, { persist: true });
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        if (!mobileQuery.matches) return;
        if (!layout.classList.contains("filters-open")) return;
        setCollapsed(true, { persist: true });
        toggleBtn.focus();
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

    initializeState();
})();
