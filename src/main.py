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
from src.visualizer import Visualizer


def main() -> int:
    """Run the simulation using the provided configuration file"""
    if len(sys.argv) not in (2, 3):
        print(
            "Usage: python -m src.main "
            "<configuration_file> [--visual]",
            file=sys.stderr,
        )
        return 1

    visual_mode = len(sys.argv) == 3 and sys.argv[2] == "--visual"

    if len(sys.argv) == 3 and not visual_mode:
        print("Invalid argument. Use --visual.", file=sys.stderr)
        return 1

    try:
        config = ConfigParser().parse_file(sys.argv[1])
        graph = Graph(config)
        nb_drones = config["nb_drones"]

        simulation = Simulation(graph, nb_drones)
        history = simulation.run()

        if visual_mode:
            visualizer = Visualizer(graph, nb_drones)
            visualizer.display(history)
        else:
            for turn in history:
                print(turn)

    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
