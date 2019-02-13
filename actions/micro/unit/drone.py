"""Everything related to scouting with drones goes here"""


class Drone:
    """Ok for now, maybe can be replaced later for zerglings"""

    def __init__(self, main):
        self.main = main
        self.rush_scout = False

    async def should_handle(self):
        """Sends the scouting drone periodically when not playing against proxies"""
        return self.main.drones and self.main.iteration % 2000 == 75 and not self.main.close_enemy_production

    async def handle(self):
        """It sends 2 drones to scout the map, for rushes or proxies"""
        for point in self.main.ordered_expansions[2: 6]:
            self.main.add_action(self.main.drones.closest_to(self.main.start_location).move(point, queue=True))
        if not self.rush_scout:
            self.rush_scout = True
            for point in self.main.enemy_start_locations:
                self.main.add_action(self.main.drones.random.move(point, queue=True))
