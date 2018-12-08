"""Everything related to controlling overlords goes here"""


class Overlord:
    """Can be expanded further to spread vision better on the map"""

    def __init__(self, ai):
        self.ai = ai
        self.first_ov_scout = False
        self.second_ov_scout = False
        self.third_ov_scout = False
        self.overlords = None
        self.locations = None
        self.selected_ov = None
        self.scout_position = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.ai
        self.overlords = local_controller.overlords.ready
        self.locations = local_controller.ordered_expansions
        return (
            self.overlords
            and self.locations
            and any(not flag for flag in (self.first_ov_scout, self.second_ov_scout, self.third_ov_scout))
        )

    async def handle(self):
        """Send the ovs to the opponents natural, our natural and near it"""
        local_controller = self.ai
        map_center = local_controller.game_info.map_center
        natural = self.locations[1]
        if not self.first_ov_scout:
            self.first_ov_scout = True
            self.selected_ov = self.overlords.first
            self.scout_position = natural
        elif not self.second_ov_scout and len(local_controller.overlords.ready) == 2:
            self.second_ov_scout = True
            self.selected_ov = self.overlords.closest_to(local_controller.townhalls.furthest_to(map_center))
            self.scout_position = natural.towards(map_center, 18)
        elif self.second_ov_scout and not self.third_ov_scout and len(local_controller.overlords.ready) == 3:
            self.third_ov_scout = True
            self.selected_ov = self.overlords.closest_to(local_controller.townhalls.first)
            self.scout_position = self.locations[-2].towards(map_center, -15)
        local_controller.add_action(self.selected_ov.move(self.scout_position))
