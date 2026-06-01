export function renderizarPanel(datos){

    document
    .getElementById("fase")
    .innerText =
    datos.fase;

    document
    .getElementById("paso")
    .innerText =
    datos.paso_actual;

    document
    .getElementById("iteraciones")
    .innerText =
    datos.historial.length;

    document
    .getElementById("error")
    .innerText =
    datos.historial.length > 0
        ? (
            datos.historial[
                datos.historial.length - 1
            ].error ?? 0
        )
        : 0;

}