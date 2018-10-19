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
        waypoints = [point for point in self.ai.expansion_locations]
        start = self.ai.start_location
        scout = self.ai.drones.closest_to(start)
        waypoints.sort(key=lambda p: ((p[0] - start[0]) ** 2 + (p[1] - start[1]) ** 2))
        for point in waypoints:
            self.ai.add_action(scout.move(point, queue=True))
