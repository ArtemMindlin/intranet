(function () {
    "use strict";

    function setupUserMenu(menuRoot) {
        var toggle = menuRoot.querySelector("[data-user-menu-toggle]");
        var dropdown = menuRoot.querySelector("[data-user-menu-dropdown]");

        if (!toggle || !dropdown) {
            return;
        }

        function menuItems() {
            return dropdown.querySelectorAll("a[href], button:not([disabled]), [role='menuitem']");
        }

        function closeMenu(returnFocus) {
            toggle.setAttribute("aria-expanded", "false");
            dropdown.hidden = true;
            menuRoot.classList.remove("is-open");
            if (returnFocus) {
                toggle.focus();
            }
        }

        function openMenu() {
            toggle.setAttribute("aria-expanded", "true");
            dropdown.hidden = false;
            menuRoot.classList.add("is-open");
        }

        toggle.addEventListener("click", function () {
            var expanded = toggle.getAttribute("aria-expanded") === "true";
            if (expanded) {
                closeMenu(false);
                return;
            }
            openMenu();
        });

        toggle.addEventListener("keydown", function (event) {
            if (event.key === "ArrowDown") {
                event.preventDefault();
                openMenu();
                var firstItem = menuItems()[0];
                if (firstItem) {
                    firstItem.focus();
                }
            }

            if (event.key === "Escape") {
                event.preventDefault();
                closeMenu(false);
            }
        });

        dropdown.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                event.preventDefault();
                closeMenu(true);
            }
        });

        dropdown.addEventListener("click", function (event) {
            var target = event.target.closest("a, button");
            if (target) {
                closeMenu(false);
            }
        });

        document.addEventListener("click", function (event) {
            if (!menuRoot.contains(event.target)) {
                closeMenu(false);
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeMenu(false);
            }
        });

        menuRoot.addEventListener("focusout", function () {
            window.setTimeout(function () {
                if (!menuRoot.contains(document.activeElement)) {
                    closeMenu(false);
                }
            }, 0);
        });
    }

    document.querySelectorAll("[data-user-menu]").forEach(setupUserMenu);
})();
