# main.py — ponto de entrada
# Será responsável por organizar a execução:
# 1. Receber o arquivo de configuração.
# 2. Chamar o parser.
# 3. Criar o grafo.
# 4. Criar e executar a simulação.
# 5. Exibir o resultado ou uma mensagem de erro.

"""Main module responsible for running the drone simulation"""

import sys
from src.graph import Graph
from src.parser import ConfigParser
from src.simulation import Simulation


def main() -> int:
    """Run the simulation using the provided configuration file"""
    if len(sys.argv) != 2:
        print(
            "Usage: python -m src.main <configuration_file>",
            file=sys.stderr,
        )
        return 1

    try:
        config = ConfigParser().parse_file(sys.argv[1])
        graph = Graph(config)
        simulation = Simulation(graph, config["nb_drones"])

        for turn in simulation.run():
            print(turn)

    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
