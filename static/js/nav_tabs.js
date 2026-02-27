(function () {
    const normalizePath = (path) => {
        if (!path) return "/";
        const trimmed = path.replace(/\/+$/, "");
        return trimmed || "/";
    };

    document.querySelectorAll("nav.nav").forEach((nav) => {
        nav.setAttribute("role", "tablist");
        if (!nav.hasAttribute("aria-label")) {
            nav.setAttribute("aria-label", "Secciones del portal");
        }
        const primaryTabs = Array.from(nav.querySelectorAll(":scope > a"));
        const moreContainer = nav.querySelector(".nav-more");
        const moreToggle = moreContainer?.querySelector(".nav-more-toggle");
        const menu = moreContainer?.querySelector(".nav-more-menu");
        const menuItems = menu ? Array.from(menu.querySelectorAll('a[role="menuitem"]')) : [];
        const tabs = moreToggle ? [...primaryTabs, moreToggle] : primaryTabs;
        if (!tabs.length) return;

        const findTabByPath = (items) => {
            const currentPath = normalizePath(window.location.pathname);
            return items.find((item) => {
                const href = item.getAttribute("href");
                if (!href) return false;
                try {
                    const itemPath = normalizePath(new URL(href, window.location.origin).pathname);
                    return itemPath === currentPath;
                } catch (err) {
                    return false;
                }
            });
        };

        let activePrimary = primaryTabs.find((tab) => tab.classList.contains("active")) || findTabByPath(primaryTabs);
        let activeMenuItem = menuItems.find((item) => item.classList.contains("active")) || findTabByPath(menuItems);

        if (!activePrimary && !activeMenuItem && primaryTabs[0]) {
            activePrimary = primaryTabs[0];
            activePrimary.classList.add("active");
        }
        if (activePrimary) {
            activePrimary.classList.add("active");
        }
        if (activeMenuItem) {
            activeMenuItem.classList.add("active");
        }

        let activeTabControl = activeMenuItem && moreToggle ? moreToggle : activePrimary;
        if (!activeTabControl && tabs[0]) {
            activeTabControl = tabs[0];
        }

        tabs.forEach((tab) => {
            const isActive = tab === activeTabControl;
            tab.setAttribute("role", "tab");
            tab.setAttribute("aria-selected", isActive ? "true" : "false");
            tab.setAttribute("tabindex", isActive ? "0" : "-1");
            if (isActive) tab.classList.add("active");
            else if (tab !== moreToggle) tab.classList.remove("active");
        });

        const setMenuOpen = (open) => {
            if (!moreContainer || !moreToggle) return;
            moreContainer.classList.toggle("open", open);
            moreToggle.setAttribute("aria-expanded", open ? "true" : "false");
        };

        if (moreToggle && menu) {
            let closeTimer = null;
            const openWithDelayProtection = () => {
                if (closeTimer) {
                    window.clearTimeout(closeTimer);
                    closeTimer = null;
                }
                setMenuOpen(true);
            };
            const closeWithDelayProtection = () => {
                if (closeTimer) {
                    window.clearTimeout(closeTimer);
                }
                closeTimer = window.setTimeout(() => {
                    setMenuOpen(false);
                    closeTimer = null;
                }, 180);
            };

            moreToggle.addEventListener("click", () => {
                setMenuOpen(!moreContainer.classList.contains("open"));
            });

            moreContainer.addEventListener("mouseenter", openWithDelayProtection);
            moreContainer.addEventListener("mouseleave", closeWithDelayProtection);

            moreToggle.addEventListener("keydown", (event) => {
                if (event.key === "ArrowDown") {
                    event.preventDefault();
                    setMenuOpen(true);
                    menuItems[0]?.focus();
                }
            });

            menu.addEventListener("keydown", (event) => {
                const currentItem = event.target.closest('a[role="menuitem"]');
                if (!currentItem) return;
                const currentIndex = menuItems.indexOf(currentItem);
                if (event.key === "Escape") {
                    event.preventDefault();
                    setMenuOpen(false);
                    moreToggle.focus();
                    return;
                }
                if (event.key === "ArrowDown" || event.key === "ArrowUp") {
                    event.preventDefault();
                    const delta = event.key === "ArrowDown" ? 1 : -1;
                    const next = (currentIndex + delta + menuItems.length) % menuItems.length;
                    menuItems[next]?.focus();
                }
            });

            document.addEventListener("click", (event) => {
                if (!moreContainer.contains(event.target)) {
                    if (closeTimer) {
                        window.clearTimeout(closeTimer);
                        closeTimer = null;
                    }
                    setMenuOpen(false);
                }
            });
        }

        nav.addEventListener("keydown", (event) => {
            const currentTab = event.target.closest('[role="tab"]');
            if (!currentTab || !nav.contains(currentTab)) return;
            const currentIndex = tabs.indexOf(currentTab);
            if (currentIndex < 0) return;

            let targetIndex = null;
            if (event.key === "ArrowRight") targetIndex = (currentIndex + 1) % tabs.length;
            if (event.key === "ArrowLeft") targetIndex = (currentIndex - 1 + tabs.length) % tabs.length;
            if (event.key === "Home") targetIndex = 0;
            if (event.key === "End") targetIndex = tabs.length - 1;
            if (targetIndex === null) return;

            event.preventDefault();
            tabs[targetIndex].focus();
        });
    });
})();
