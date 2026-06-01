import { getSimulacion }
from "../api/simulacionApi.js";

export async function useVisualizador(){

    const simulacion =
    await getSimulacion();

    return simulacion;

}