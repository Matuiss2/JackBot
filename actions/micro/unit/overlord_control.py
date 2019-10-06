"""Everything related to controlling overlords goes here"""


class OverlordControl:
    """Can be expanded further to spread vision better on the map and be more dynamic(run away from enemies f.e)"""

    def __init__(self, main):
        self.main = main
        self.first_ov_scout = self.second_ov_scout = self.third_ov_scout = False
        self.ready_overlords = self.scout_position = self.selected_ov = None

    async def should_handle(self):
        """Requirements to move the overlords"""
        self.ready_overlords = self.main.overlords.ready
        return self.main.overlords.ready and any(
            not flag for flag in (self.first_ov_scout, self.second_ov_scout, self.third_ov_scout)
        )

    async def handle(self):
        """Send the ovs to the center, our natural and near our natural(to check proxies and incoming attacks)"""
        map_center = self.main.game_info.map_center
        natural = self.main.ordered_expansions[1]
        if not self.first_ov_scout:
            self.first_ov_scout = True
            self.selected_ov = self.ready_overlords.first
            self.scout_position = natural
        elif not self.second_ov_scout and self.main.ready_overlord_amount == 2:
            self.second_ov_scout = True
            self.selected_ov = self.ready_overlords.closest_to(self.main.furthest_townhall_to_center)
            self.scout_position = natural.towards(map_center, 18)
        elif self.second_ov_scout and not self.third_ov_scout and self.main.ready_overlord_amount == 3:
            self.third_ov_scout = True
            self.selected_ov = self.ready_overlords.closest_to(self.main.townhalls.first)
            self.scout_position = map_center
        self.main.add_action(self.selected_ov.move(self.scout_position))
