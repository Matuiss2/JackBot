from . import buildings_demolition, micro_main, worker_distribution


def get_army_and_building_commands(command):
    return (
        buildings_demolition.BuildingsDemolition(command),
        micro_main.ArmyControl(command),
        worker_distribution.WorkerDistribution(command),
    )
