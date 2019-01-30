"""Everything related to scouting with drones goes here"""


class Drone:
    """Ok for now, maybe can be replaced later for zerglings"""

    def __init__(self, main):
        self.controller = main
        self.rush_scout = False
        self.drones = None

    async def should_handle(self):
        """Sends the scouting drone periodically when not playing against proxies"""
        local_controller = self.controller
        self.drones = local_controller.drones
        return self.drones and local_controller.iteration % 2000 == 75 and not local_controller.close_enemy_production

    async def handle(self):
        """It sends 2 drones to scout the map, for rushes or proxies"""
        local_controller = self.controller
        scout = self.drones.closest_to(local_controller.start_location)
        expansion_locations = local_controller.ordered_expansions
        for point in expansion_locations[2:]:
            local_controller.add_action(scout.move(point, queue=True))
        if not self.rush_scout:
            self.rush_scout = True
            local_controller.add_action(self.drones.random.move(expansion_locations[-1]))
