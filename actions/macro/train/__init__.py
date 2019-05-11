from . import (
    drone_creation,
    hydra_creation,
    mutalisk_creation,
    overlord_creation,
    overseer_creation,
    queen_creation,
    ultralisk_creation,
    zergling_creation,
)


def get_train_commands(command):
    return (
        drone_creation.DroneCreation(command),
        hydra_creation.HydraliskCreation(command),
        mutalisk_creation.MutaliskCreation(command),
        overlord_creation.OverlordCreation(command),
        overseer_creation.OverseerCreation(command),
        queen_creation.QueenCreation(command),
        ultralisk_creation.UltraliskCreation(command),
        zergling_creation.ZerglingCreation(command),
    )
