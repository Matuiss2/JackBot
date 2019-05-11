from . import proxy_defense, worker_rush_defense


def get_cheese_defense_commands(command):
    return proxy_defense.ProxyDefense(command), worker_rush_defense.WorkerRushDefense(command)
