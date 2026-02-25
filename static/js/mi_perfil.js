document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("perfilEditableForm");
    if (!form) {
        return;
    }

    const editableFields = Array.from(
        form.querySelectorAll(".js-editable-field")
    );
    const editButton = document.getElementById("editarDatosBtn");
    const saveButton = document.getElementById("guardarCambiosBtn");
    const cancelButton = document.getElementById("cancelarEdicionBtn");

    const initialValues = new Map();
    editableFields.forEach((field) => {
        initialValues.set(field.name, field.dataset.initial || "");
    });

    let isEditing = form.dataset.startEditing === "1";

    const hasChanges = () =>
        editableFields.some(
            (field) => (field.value || "").trim() !== (initialValues.get(field.name) || "").trim()
        );

    const syncSaveState = () => {
        if (!saveButton) {
            return;
        }
        saveButton.disabled = !hasChanges();
    };

    const setEditingMode = (enabled) => {
        isEditing = enabled;
        form.classList.toggle("is-editing", enabled);

        editableFields.forEach((field) => {
            field.disabled = !enabled;
        });

        if (editButton) {
            editButton.classList.toggle("is-hidden", enabled);
        }
        if (saveButton) {
            saveButton.classList.toggle("is-hidden", !enabled);
        }
        if (cancelButton) {
            cancelButton.classList.toggle("is-hidden", !enabled);
        }

        if (enabled) {
            syncSaveState();
        } else if (saveButton) {
            saveButton.disabled = true;
            saveButton.textContent = "Guardar cambios";
        }
    };

    const restoreInitialValues = () => {
        editableFields.forEach((field) => {
            field.value = initialValues.get(field.name) || "";
        });
    };

    editableFields.forEach((field) => {
        field.addEventListener("input", syncSaveState);
        field.addEventListener("change", syncSaveState);
    });

    if (editButton) {
        editButton.addEventListener("click", () => {
            setEditingMode(true);
            if (editableFields.length > 0) {
                editableFields[0].focus();
            }
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener("click", () => {
            restoreInitialValues();
            setEditingMode(false);
        });
    }

    form.addEventListener("submit", (event) => {
        if (!isEditing || !hasChanges()) {
            event.preventDefault();
            return;
        }
        if (saveButton) {
            saveButton.disabled = true;
            saveButton.textContent = "Guardando...";
        }
    });

    setEditingMode(isEditing);
});
