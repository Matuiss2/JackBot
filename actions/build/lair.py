"""Everything related to building logic for the lairs goes here"""
from sc2.constants import LAIR, UPGRADETOLAIR_LAIR


class BuildLair:
    """Maybe can be improved, probably its a bit greedy"""

    def __init__(self, main):
        self.controller = main
        self.selected_hatchery = None

    async def should_handle(self):
        """Builds the lair"""
        local_controller = self.controller
        self.selected_hatchery = local_controller.hatcheries.ready.idle
        return (
            not (local_controller.lairs or local_controller.hives)
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.evochambers.ready) >= 2)
            )
            and local_controller.can_build_unique(LAIR, local_controller.caverns, self.selected_hatchery)
            and not local_controller.already_pending(LAIR, all_units=True)
        )

    async def handle(self):
        """Finishes the action of making the lair choosing the safest base"""
        local_controller = self.controller
        local_controller.add_action(
            self.selected_hatchery.furthest_to(local_controller.game_info.map_center)(UPGRADETOLAIR_LAIR)
        )
        return True
