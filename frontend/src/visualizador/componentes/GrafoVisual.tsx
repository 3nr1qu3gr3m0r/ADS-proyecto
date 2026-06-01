export function renderizarGrafo(
    canvas,
    red,
    simulacion
){

    const ctx =
    canvas.getContext("2d");

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    let valores = {};

    if(
        simulacion.historial &&
        simulacion.historial.length > 0
    ){

        const ultimoResultado =
        simulacion.historial[
            simulacion.historial.length - 1
        ];

        valores =
        ultimoResultado.valores_nodos;
    }

    red.aristas.forEach(arista=>{

        const origen =
        red.nodos.find(
            n=>n.id===arista.origen
        );

        const destino =
        red.nodos.find(
            n=>n.id===arista.destino
        );

        ctx.beginPath();

        ctx.moveTo(
            origen.x,
            origen.y
        );

        ctx.lineTo(
            destino.x,
            destino.y
        );

        ctx.strokeStyle =
        "#94a3b8";

        ctx.lineWidth = 5;

        ctx.stroke();

    });

    red.nodos.forEach(nodo=>{

        const valor =
        valores[nodo.id] || 0;

        let color =
        "#3b82f6";

        if(valor > 0.8){

            color =
            "#ef4444";

        }else if(valor > 0.5){

            color =
            "#f59e0b";

        }else if(valor > 0.2){

            color =
            "#22c55e";

        }

        ctx.beginPath();

        ctx.arc(
            nodo.x,
            nodo.y,
            45,
            0,
            Math.PI * 2
        );

        ctx.fillStyle =
        color;

        ctx.fill();

        ctx.lineWidth = 4;

        ctx.strokeStyle =
        "white";

        ctx.stroke();

        ctx.fillStyle =
        "white";

        ctx.font =
        "bold 18px Arial";

        ctx.fillText(
            nodo.id,
            nodo.x - 35,
            nodo.y + 70
        );

        ctx.font =
        "16px Arial";

        ctx.fillText(
            valor.toFixed(2),
            nodo.x - 15,
            nodo.y + 5
        );

    });

}