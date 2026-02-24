(function () {
    const selects = Array.from(document.querySelectorAll("select.js-combobox"));
    if (!selects.length) return;

    function normalize(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    class SelectCombobox {
        constructor(select, index) {
            this.select = select;
            this.index = index;
            this.root = null;
            this.input = null;
            this.list = null;
            this.options = [];
            this.filteredOptions = [];
            this.activeIndex = -1;
            this.uid = select.id || `combobox-${index + 1}`;
        }

        init() {
            if (this.select.dataset.comboboxReady === "1") return;
            this.select.dataset.comboboxReady = "1";

            this.options = Array.from(this.select.options).map((option, index) => ({
                value: option.value,
                label: option.textContent.trim(),
                index,
                disabled: option.disabled,
            }));
            this.filteredOptions = this.options.slice();

            this.buildDom();
            this.bindEvents();
            this.syncInputToSelect();
            this.refresh("");
        }

        buildDom() {
            const root = document.createElement("div");
            root.className = "select-combobox";
            root.id = `${this.uid}-combobox`;

            const input = document.createElement("input");
            input.type = "text";
            const passthroughClasses = Array.from(this.select.classList).filter(
                (className) => className !== "js-combobox"
            );
            input.classList.add("select-combobox__search");
            passthroughClasses.forEach((className) => input.classList.add(className));
            input.id = `${this.uid}-search`;
            input.autocomplete = "off";
            input.setAttribute("role", "combobox");
            input.setAttribute("aria-autocomplete", "list");
            input.setAttribute("aria-expanded", "false");
            input.setAttribute("aria-haspopup", "listbox");
            input.setAttribute("aria-controls", `${this.uid}-list`);
            input.placeholder =
                this.select.dataset.comboboxPlaceholder || "Buscar...";

            if (this.select.disabled) {
                input.disabled = true;
                root.classList.add("is-disabled");
            }

            const list = document.createElement("div");
            list.className = "select-combobox__list";
            list.id = `${this.uid}-list`;
            list.setAttribute("role", "listbox");

            this.select.classList.add("select-combobox__native");

            this.select.parentNode.insertBefore(root, this.select);
            root.appendChild(this.select);
            root.appendChild(input);
            root.appendChild(list);

            if (this.select.id) {
                const labelSelector = `label[for="${this.select.id}"]`;
                const labels = document.querySelectorAll(labelSelector);
                labels.forEach((label) => label.setAttribute("for", input.id));
            }

            this.root = root;
            this.input = input;
            this.list = list;
        }

        bindEvents() {
            if (!this.input || !this.list) return;

            this.input.addEventListener("focus", () => {
                this.refresh(this.input.value);
                this.open();
            });

            this.input.addEventListener("click", () => {
                this.refresh(this.input.value);
                this.open();
            });

            this.input.addEventListener("input", () => {
                this.refresh(this.input.value);
                if (this.filteredOptions.length > 0) {
                    this.setActive(0);
                } else {
                    this.setActive(-1);
                }
                this.open();
            });

            this.input.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    this.close();
                    this.syncInputToSelect();
                    return;
                }

                if (event.key === "ArrowDown") {
                    if (!this.isOpen()) {
                        this.refresh(this.input.value);
                        this.open();
                    }
                    this.setActive(this.activeIndex + 1);
                    event.preventDefault();
                    return;
                }

                if (event.key === "ArrowUp") {
                    if (!this.isOpen()) {
                        this.refresh(this.input.value);
                        this.open();
                    }
                    this.setActive(this.activeIndex - 1);
                    event.preventDefault();
                    return;
                }

                if (event.key === "Enter" && this.isOpen()) {
                    if (this.activeIndex >= 0 && this.filteredOptions[this.activeIndex]) {
                        this.selectByValue(this.filteredOptions[this.activeIndex].value);
                    }
                    event.preventDefault();
                }
            });

            this.list.addEventListener("mousedown", (event) => {
                event.preventDefault();
            });

            this.list.addEventListener("click", (event) => {
                const optionEl = event.target.closest(".select-combobox__option");
                if (!optionEl || optionEl.dataset.disabled === "true") return;
                this.selectByValue(optionEl.dataset.value || "");
            });

            this.select.addEventListener("change", () => {
                this.syncInputToSelect();
            });
        }

        scoreAndSort(query) {
            const q = normalize(query);
            if (!q) return this.options.slice();

            const starts = [];
            const includes = [];
            const rest = [];

            for (const item of this.options) {
                const label = normalize(item.label);
                if (label.startsWith(q)) {
                    starts.push(item);
                } else if (label.includes(q)) {
                    includes.push(item);
                } else {
                    rest.push(item);
                }
            }

            return starts.concat(includes, rest);
        }

        refresh(query) {
            this.filteredOptions = this.scoreAndSort(query);
            this.render();
        }

        render() {
            const fragment = document.createDocumentFragment();
            const selectedValue = this.select.value;

            this.filteredOptions.forEach((item) => {
                const optionEl = document.createElement("div");
                optionEl.className = "select-combobox__option";
                optionEl.id = `${this.uid}-option-${item.index}`;
                optionEl.setAttribute("role", "option");
                optionEl.setAttribute("data-value", item.value);
                optionEl.setAttribute("data-disabled", String(item.disabled));
                optionEl.setAttribute("aria-selected", String(item.value === selectedValue));
                optionEl.textContent = item.label;
                if (item.disabled) optionEl.classList.add("is-disabled");
                fragment.appendChild(optionEl);
            });

            this.list.innerHTML = "";
            this.list.appendChild(fragment);
            if (this.activeIndex >= this.filteredOptions.length) {
                this.activeIndex = -1;
            }
            this.setActive(this.activeIndex);
        }

        getSelectedOption() {
            return (
                this.options.find((item) => item.value === this.select.value) ||
                this.options[0] ||
                null
            );
        }

        syncInputToSelect() {
            const selected = this.getSelectedOption();
            this.input.value = selected ? selected.label : "";
        }

        selectByValue(value) {
            const next = this.options.find((item) => item.value === value && !item.disabled);
            if (!next) return;

            this.select.value = next.value;
            this.syncInputToSelect();
            this.select.dispatchEvent(new Event("input", { bubbles: true }));
            this.select.dispatchEvent(new Event("change", { bubbles: true }));
            this.close();
        }

        isOpen() {
            return this.list.classList.contains("is-open");
        }

        open() {
            if (!this.filteredOptions.length) {
                this.list.classList.remove("is-open");
                this.input.setAttribute("aria-expanded", "false");
                return;
            }
            this.list.classList.add("is-open");
            this.input.setAttribute("aria-expanded", "true");
        }

        close() {
            this.list.classList.remove("is-open");
            this.input.setAttribute("aria-expanded", "false");
            this.input.removeAttribute("aria-activedescendant");
            this.activeIndex = -1;
            this.setActive(-1);
        }

        setActive(index) {
            const items = Array.from(this.list.querySelectorAll(".select-combobox__option"));
            if (!items.length || index < 0) {
                this.activeIndex = -1;
                items.forEach((item) => item.classList.remove("is-active"));
                this.input.removeAttribute("aria-activedescendant");
                return;
            }

            const lastIndex = items.length - 1;
            if (index > lastIndex) index = 0;
            if (index < 0) index = lastIndex;

            this.activeIndex = index;
            items.forEach((item, itemIndex) => {
                item.classList.toggle("is-active", itemIndex === this.activeIndex);
            });

            const current = items[this.activeIndex];
            if (!current) return;

            this.input.setAttribute("aria-activedescendant", current.id);
            current.scrollIntoView({ block: "nearest" });
        }
    }

    const instances = selects.map((select, index) => {
        const instance = new SelectCombobox(select, index);
        instance.init();
        return instance;
    });

    document.addEventListener("click", (event) => {
        instances.forEach((instance) => {
            if (!instance.root.contains(event.target)) {
                instance.close();
                instance.syncInputToSelect();
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        instances.forEach((instance) => instance.close());
    });
})();
