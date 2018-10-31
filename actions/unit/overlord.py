"""Everything related to controlling overlords goes here"""


class Overlord:
    """Can be expanded further to spread vision better on the map"""

    def __init__(self, ai):
        self.ai = ai
        self.first_ov_scout = False
        self.second_ov_scout = False
        self.third_ov_scout = False

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return local_controller.overlords and local_controller.enemy_start_locations

    async def handle(self, iteration):
        """Send the ovs to the center and near the natural"""
        local_controller = self.ai
        action = local_controller.add_action
        map_center = local_controller.game_info.map_center
        if not self.first_ov_scout:
            first_ov = local_controller.overlords.first
            self.first_ov_scout = True
            action(first_ov.move(local_controller.ordered_expansions[-2].towards(map_center, -15)))
        elif not self.second_ov_scout and len(local_controller.overlords.ready) == 2:
            second_ov = local_controller.overlords.ready.closest_to(local_controller.townhalls.first)
            self.second_ov_scout = True
            action(second_ov.move(local_controller.ordered_expansions[1]))
        elif self.second_ov_scout and not self.third_ov_scout and len(local_controller.overlords.ready) == 3:
            self.third_ov_scout = True
            third_ov = local_controller.overlords.ready.closest_to(local_controller.townhalls.furthest_to(map_center))
            action(third_ov.move(local_controller.ordered_expansions[1].towards(map_center, 18)))
