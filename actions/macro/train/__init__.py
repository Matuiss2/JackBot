""" Group all classes from macro/train"""
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


def get_train_commands(cmd):
    """ Getter for all commands from macro/train"""
    return (
        drone_creation.DroneCreation(cmd),
        hydra_creation.HydraliskCreation(cmd),
        mutalisk_creation.MutaliskCreation(cmd),
        overlord_creation.OverlordCreation(cmd),
        overseer_creation.OverseerCreation(cmd),
        queen_creation.QueenCreation(cmd),
        ultralisk_creation.UltraliskCreation(cmd),
        zergling_creation.ZerglingCreation(cmd),
    )
