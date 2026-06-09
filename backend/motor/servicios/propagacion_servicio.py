from motor.servicios.construccion_matriz import EPiCAdapter, VisualizerAdapter
from motor.algoritmos.engine import EPiCEngine


def calcular_propagacion(network_dict: dict) -> dict:
    model = EPiCAdapter.network_to_model(network_dict)
    engine = EPiCEngine()
    propagation_state = engine.run(model)
    return VisualizerAdapter.build_result(model, propagation_state)
