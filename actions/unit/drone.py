class Drone:
    def __init__(self, ai):
        self.ai = ai
        self.scout_tag = None

    async def should_handle(self, iteration):
        return not self.scout_tag and self.ai.drones and iteration % 2000 == 400

    async def handle(self, iteration):
        """It sends a drone to scout the map, starting with the closest place then going base by base to the furthest"""
        waypoints = [point for point in self.ai.expansion_locations]
        start = self.ai.start_location
        scout = self.ai.drones.closest_to(start)
        self.scout_tag = scout.tag
        waypoints.sort(key=lambda p: ((p[0] - start[0]) ** 2 + (p[1] - start[1]) ** 2))
        for point in waypoints:
            self.ai.actions.append(scout.move(point, queue=True))
