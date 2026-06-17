from motor.dominio.modelos import Variable, Connective, EPiCModel
from motor.algoritmos.constantes import NAME_TO_VALUE, VALUE_NAMES


class EPiCAdapter:

    @staticmethod
    def network_to_model(network):

        variables = []
        connectives = []

        node_map = {}

        for node in network["nodos"]:

            node_map[node["id"]] = node

            if node["tipo"] == "VARIABLE":

                props = node.get("propiedades", {})

                value = NAME_TO_VALUE.get(
                    props.get("valor", "N"),
                    NAME_TO_VALUE["N"]
                )

                variables.append(
                    Variable(
                        id=node["id"],
                        name=node["etiqueta"],
                        initial_value=value,
                        current_value=value,
                        is_premise=props.get("premisa", False)
                    )
                )

        incoming = {}

        outgoing = {}

        for edge in network["aristas"]:

            outgoing.setdefault(
                edge["idOrigen"],
                []
            ).append(edge["idDestino"])

            incoming.setdefault(
                edge["idDestino"],
                []
            ).append(edge["idOrigen"])

        for node in network["nodos"]:

            ntype = node["tipo"]

            if ntype not in (
                "AND",
                "OR",
                "NOT",
                "IMP"
            ):
                continue

            inputs = incoming.get(node["id"], [])
            outputs = outgoing.get(node["id"], [])

            if not outputs:
                continue

            output_id = outputs[0]

            ctype_map = {
                "AND": "conjunction",
                "OR": "disjunction",
                "NOT": "negation",
                "IMP": "implication"
            }

            connectives.append(
                Connective(
                    id=node["id"],
                    type=ctype_map[ntype],
                    input_ids=inputs,
                    output_id=output_id
                )
            )

        return EPiCModel(
            id=network["id"],
            variables=variables,
            connectives=connectives
        )


class VisualizerAdapter:

    @staticmethod
    def build_result(model, propagation_state):

        return {

            "redId": model.id,

            "iteraciones": propagation_state.iteration,

            "convergido": propagation_state.stable,

            "error": None,

            "valoresNodos": {

                var.id:
                VALUE_NAMES[var.current_value]

                for var in model.variables
            }
        }
