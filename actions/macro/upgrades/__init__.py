""" Group all classes from macro/upgrades"""
from . import cavern_upgrades, evochamber_upgrades, hydraden_upgrades, spawning_pool_upgrades


def get_upgrade_commands(command):
    """ Getter for all commands from macro/upgrades"""
    return (
        cavern_upgrades.CavernUpgrades(command),
        evochamber_upgrades.EvochamberUpgrades(command),
        hydraden_upgrades.HydradenUpgrades(command),
        spawning_pool_upgrades.SpawningPoolUpgrades(command),
    )
