"""Everything related to scouting with drones goes here"""


class Drone:
    """Ok for now, maybe can be replaced later for zerglings"""

    def __init__(self, main):
        self.controller = main
        self.rush_scout = False
        self.drones = None

    async def should_handle(self):
        """Sends the scouting drone periodically when not playing against proxies"""
        self.drones = self.controller.drones
        return self.drones and self.controller.iteration % 2000 == 75 and not self.controller.close_enemy_production

    async def handle(self):
        """It sends 2 drones to scout the map, for rushes or proxies"""
        scout = self.drones.closest_to(self.controller.start_location)
        expansion_locations = self.controller.ordered_expansions
        for point in expansion_locations[2:]:
            self.controller.add_action(scout.move(point, queue=True))
        if not self.rush_scout:
            self.rush_scout = True
            self.controller.add_action(self.drones.random.move(self.controller.enemy_start_locations[0]))
