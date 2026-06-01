from simulador.servicios.estado_simulacion import (
    EstadoSimulacion,
    ResultadoPropagacion
)


class SimulacionServicio:

    def __init__(self):

        self.estado = EstadoSimulacion()

    def iniciar_simulacion(self):

        self.estado.fase = "corriendo"

        self.estado.paso_actual = 0

        self.estado.historial = []

        return self.estado

    def avanzar_paso(self):

        self.estado.paso_actual += 1

        resultado = ResultadoPropagacion(

            red_id="red-001",

            iteraciones=self.estado.paso_actual,

            valores_nodos={

                "nodo-001": round(
                    min(
                        1.0,
                        self.estado.paso_actual * 0.20
                    ),
                    2
                ),

                "nodo-002": round(
                    min(
                        1.0,
                        self.estado.paso_actual * 0.15
                    ),
                    2
                ),

                "nodo-003": round(
                    min(
                        1.0,
                        self.estado.paso_actual * 0.10
                    ),
                    2
                )
            },

            convergido=
            self.estado.paso_actual >= 5
        )

        self.estado.historial.append(resultado)

        if resultado.convergido:

            self.estado.fase = "completado"

        return self.estado

    def pausar(self):

        self.estado.fase = "pausado"

        return self.estado

    def obtener_estado(self):

        return self.estado