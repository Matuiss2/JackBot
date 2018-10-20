"""Everything related to scouting with drones goes here"""


class Drone:
    """Ok for now, maybe can be replaced later for zerglings"""

    def __init__(self, ai):
        self.ai = ai
        self.scout_tag = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return self.ai.drones and iteration % 2000 == 75 and not self.ai.close_enemy_production

    async def handle(self, iteration):
        """It sends a drone to scout the map, starting with the closest place then going base by base to the furthest"""
        scout = self.ai.drones.closest_to(self.ai.start_location)
        for point in self.ai.ordered_expansions:
            self.ai.add_action(scout.move(point, queue=True))
