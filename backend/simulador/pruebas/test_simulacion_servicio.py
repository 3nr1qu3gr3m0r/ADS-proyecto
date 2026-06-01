from simulador.servicios.simulacion_servicio import (
    SimulacionServicio
)


def test_iniciar_simulacion():

    servicio = SimulacionServicio()

    estado = servicio.iniciar_simulacion()

    assert estado.fase == "corriendo"


def test_avanzar_paso():

    servicio = SimulacionServicio()

    servicio.iniciar_simulacion()

    estado = servicio.avanzar_paso()

    assert estado.paso_actual == 1


def test_pausar():

    servicio = SimulacionServicio()

    servicio.iniciar_simulacion()

    estado = servicio.pausar()

    assert estado.fase == "pausado"