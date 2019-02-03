"""Everything related to controlling overlords goes here"""


class Overlord:
    """Can be expanded further to spread vision better on the map and be more dynamic(run away from enemies f.e)"""

    def __init__(self, main):
        self.controller = main
        self.first_ov_scout = self.second_ov_scout = self.third_ov_scout = False
        self.selected_ov = self.scout_position = self.overlords = None

    async def should_handle(self):
        """Requirements to move the overlords"""
        self.overlords = self.controller.overlords.ready
        return self.overlords and any(
            not flag for flag in (self.first_ov_scout, self.second_ov_scout, self.third_ov_scout)
        )

    async def handle(self):
        """Send the ovs to the center, our natural and near our natural(to check proxies and incoming attacks)"""
        map_center = self.controller.game_info.map_center
        natural = self.controller.ordered_expansions[0]
        if not self.first_ov_scout:
            self.first_ov_scout = True
            self.selected_ov = self.overlords.first
            self.scout_position = natural
        elif not self.second_ov_scout and len(self.controller.overlords.ready) == 2:
            self.second_ov_scout = True
            self.selected_ov = self.overlords.closest_to(self.controller.townhalls.furthest_to(map_center))
            self.scout_position = natural.towards(map_center, 18)
        elif self.second_ov_scout and not self.third_ov_scout and len(self.controller.overlords.ready) == 3:
            self.third_ov_scout = True
            self.selected_ov = self.overlords.closest_to(self.controller.townhalls.first)
            self.scout_position = map_center
        self.controller.add_action(self.selected_ov.move(self.scout_position))
