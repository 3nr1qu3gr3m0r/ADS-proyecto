import { renderizarPanel }
from "./PanelResultados.tsx";

import { renderizarGrafo }
from "./GrafoVisual.tsx";

export function iniciarControles(
    simulacion,
    red
){

    let intervalo = null;

    document
    .getElementById("btnPlay")
    .onclick = ()=>{

        if(intervalo)
            return;

        intervalo =
        setInterval(()=>{

            avanzar();

        },1000);

    };

    document
    .getElementById("btnPause")
    .onclick = ()=>{

        clearInterval(
            intervalo
        );

        intervalo = null;

    };

    document
    .getElementById("btnPaso")
    .onclick = ()=>{

        avanzar();

    };

    document
    .getElementById("btnReset")
    .onclick = ()=>{

        clearInterval(
            intervalo
        );

        intervalo = null;

        simulacion.pasoActual = 0;

        simulacion.iteraciones = 0;

        simulacion.error = 0;

        simulacion.valoresNodos = {

            "nodo-001":0.20,
            "nodo-002":0.10,
            "nodo-003":0.10,
            "nodo-004":0.10

        };

        actualizar();

    };

    function avanzar(){

        simulacion.pasoActual++;

        simulacion.iteraciones++;

        simulacion.error =
        (
            Math.random()*0.1
        ).toFixed(4);

        if(simulacion.pasoActual===1)
            simulacion.valoresNodos["nodo-002"]=0.45;

        if(simulacion.pasoActual===2)
            simulacion.valoresNodos["nodo-003"]=0.70;

        if(simulacion.pasoActual===3)
            simulacion.valoresNodos["nodo-004"]=0.95;

        actualizar();

        agregarEvento(
            "Paso "
            +
            simulacion.pasoActual
        );

    }

    function actualizar(){

        renderizarPanel(
            simulacion
        );

        renderizarGrafo(
            document.getElementById(
                "canvas"
            ),
            red,
            simulacion
        );

    }

    function agregarEvento(
        texto
    ){

        const lista =
        document.getElementById(
            "listaEventos"
        );

        const li =
        document.createElement(
            "li"
        );

        li.innerText =
        texto;

        lista.prepend(
            li
        );

    }

}