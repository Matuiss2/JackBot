"""Everything related to building logic for the lairs goes here"""
from sc2.constants import LAIR, UPGRADETOLAIR_LAIR


class BuildLair:
    """Maybe can be improved, probably its a bit greedy it leaves a gap where the bot is vulnerable"""

    def __init__(self, main):
        self.controller = main
        self.selected_hatchery = None

    async def should_handle(self):
        """Requirements to build the lair"""
        self.selected_hatchery = self.controller.hatcheries.ready.idle
        return (
            not (self.controller.lairs or self.controller.hives)
            and (
                len(self.controller.townhalls) >= 3
                or (self.controller.close_enemy_production and len(self.controller.evochambers.ready) >= 2)
            )
            and self.controller.can_build_unique(LAIR, self.controller.caverns, self.selected_hatchery)
            and not self.controller.already_pending(LAIR, all_units=True)
        )

    async def handle(self):
        """Finishes the action of making the lair choosing the safest available base"""
        self.controller.add_action(
            self.controller.furthest_townhall_to_center(UPGRADETOLAIR_LAIR)
        )
        return True
