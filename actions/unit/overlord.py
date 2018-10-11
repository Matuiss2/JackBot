class Overlord:
    def __init__(self, ai):
        self.ai = ai
        self.first_ov_scout = False
        self.second_ov_scout = False

    async def should_handle(self, iteration):
        return self.ai.overlords and self.ai.enemy_start_locations

    async def handle(self, iteration):
        # enemy_main = self.ai.enemy_start_locations[0]  # point2
        # enemy_natural = min(
        #    self.ai.ordered_expansions,
        #    key=lambda expo: (expo.x - enemy_main.x) ** 2 + (expo.y - enemy_main.y) ** 2
        #    if expo.x - enemy_main.x != 0 and expo.y - enemy_main.y != 0
        #   else 10 ** 10,
        # )
        if not self.first_ov_scout:
            self.first_ov_scout = True
            waypoints = [point for point in self.ai.expansion_locations]
            start = self.ai.start_location
            natural = sorted(waypoints, key=lambda p: ((p[0] - start[0]) ** 2 + (p[1] - start[1]) ** 2))[1]
            self.ai.actions.append(self.ai.overlords.first.move(natural.towards(self.ai._game_info.map_center, 10)))
        elif not self.second_ov_scout and len(self.ai.overlords.ready) == 2:
            second_ov = self.ai.overlords.ready.closest_to(self.ai.townhalls.first)
            self.second_ov_scout = True
            self.ai.actions.append(second_ov.move(self.ai._game_info.map_center))
        # self.ai.actions.append(self.ai.overlords.first.move(enemy_natural.towards(enemy_main, -11)))
