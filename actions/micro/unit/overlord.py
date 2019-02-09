"""Everything related to controlling overlords goes here"""


class Overlord:
    """Can be expanded further to spread vision better on the map and be more dynamic(run away from enemies f.e)"""

    def __init__(self, main):
        self.main = main
        self.first_ov_scout = self.second_ov_scout = self.third_ov_scout = False
        self.selected_ov = self.scout_position = None

    async def should_handle(self):
        """Requirements to move the overlords"""
        return self.main.overlords.ready and any(
            not flag for flag in (self.first_ov_scout, self.second_ov_scout, self.third_ov_scout)
        )

    async def handle(self):
        """Send the ovs to the center, our natural and near our natural(to check proxies and incoming attacks)"""
        map_center = self.main.game_info.map_center
        natural = self.main.ordered_expansions[0]
        if not self.first_ov_scout:
            self.first_ov_scout = True
            self.selected_ov = self.main.overlords.ready.first
            self.scout_position = natural
        elif not self.second_ov_scout and self.main.ready_overlord_amount == 2:
            self.second_ov_scout = True
            self.selected_ov = self.main.overlords.ready.closest_to(self.main.furthest_townhall_to_center)
            self.scout_position = natural.towards(map_center, 18)
        elif self.second_ov_scout and not self.third_ov_scout and self.main.ready_overlord_amount == 3:
            self.third_ov_scout = True
            self.selected_ov = self.main.overlords.ready.closest_to(self.main.townhalls.first)
            self.scout_position = map_center
        self.main.add_action(self.selected_ov.move(self.scout_position))
