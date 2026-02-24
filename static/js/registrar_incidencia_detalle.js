(function () {
    const textarea =
        document.getElementById("detalleIncidencia") ||
        document.querySelector("textarea[name='detalle']");
    const counter = document.getElementById("detalleCounter");

    if (!textarea || !counter) return;

    function updateCounter() {
        const length = textarea.value.length;
        const max = textarea.getAttribute("maxlength");
        counter.textContent = max ? `${length} / ${max}` : `${length} caracteres`;
    }

    updateCounter();
    textarea.addEventListener("input", updateCounter);
})();
