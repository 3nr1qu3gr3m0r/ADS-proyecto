import { redDemo }
from "./mocks/redDemo.js";

import { useVisualizador }
from "./hooks/useVisualizador.js";

import { renderizarPanel }
from "./componentes/PanelResultados.js";

import { renderizarGrafo }
from "./componentes/GrafoVisual.js";

import { iniciarControles }
from "./componentes/ControlSimulacion.js";

async function iniciar(){

    try{

        const simulacion =
        await useVisualizador();

        renderizarPanel(
            simulacion
        );

        renderizarGrafo(
            document.getElementById(
                "canvas"
            ),
            redDemo,
            simulacion
        );

        iniciarControles(
            simulacion,
            redDemo
        );

    }
    catch(error){

        console.error(error);

        alert(
            "Error: "
            + error.message
        );

    }

}

iniciar();