"""Everything related to scouting with drones goes here"""


class Drone:
    """Ok for now, maybe can be replaced later for zerglings"""

    def __init__(self, ai):
        self.ai = ai
        self.drones = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.ai
        self.drones = local_controller.drones
        return self.drones and local_controller.iteration % 2000 == 75 and not local_controller.close_enemy_production

    async def handle(self):
        """It sends a drone to scout the map, starting with the closest place then going base by base to the furthest"""
        local_controller = self.ai
        scout = self.drones.random
        for point in local_controller.ordered_expansions:
            local_controller.add_action(scout.move(point, queue=True))
