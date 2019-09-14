""" Group all classes from anti_cheese"""
from . import proxy_defense, worker_rush_defense


def get_cheese_defense_commands(cmd):
    """ Getter for all commands from anti_cheese"""
    return proxy_defense.ProxyDefense(cmd), worker_rush_defense.WorkerRushDefense(cmd)
