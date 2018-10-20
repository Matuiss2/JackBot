"""Everything related to controlling overlords goes here"""


class Overlord:
    """Can be expanded further to spread vision better on the map"""

    def __init__(self, ai):
        self.ai = ai
        self.first_ov_scout = False
        self.second_ov_scout = False

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return self.ai.overlords and self.ai.enemy_start_locations

    async def handle(self, iteration):
        """Send the ovs to the center and near the natural"""
        action = self.ai.add_action
        map_center = self.ai._game_info.map_center
        # enemy_main = self.ai.enemy_start_locations[0]  # point2
        # enemy_natural = min(
        #    self.ai.ordered_expansions,
        #    key=lambda expo: (expo.x - enemy_main.x) ** 2 + (expo.y - enemy_main.y) ** 2
        #    if expo.x - enemy_main.x != 0 and expo.y - enemy_main.y != 0
        #   else 10 ** 10,
        # )
        if not self.first_ov_scout:
            self.first_ov_scout = True
            action(
                self.ai.overlords.first.move(self.ai.ordered_expansions[1].towards(map_center, 18))
            )
        elif not self.second_ov_scout and len(self.ai.overlords.ready) == 2:
            second_ov = self.ai.overlords.ready.closest_to(self.ai.townhalls.first)
            self.second_ov_scout = True
            action(second_ov.move(map_center))
        # action(self.ai.overlords.first.move(enemy_natural.towards(enemy_main, -11)))
