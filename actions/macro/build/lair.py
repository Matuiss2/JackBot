"""Everything related to building logic for the lairs goes here"""
from sc2.constants import LAIR, UPGRADETOLAIR_LAIR


class BuildLair:
    """Maybe can be improved, probably its a bit greedy it leaves a gap where the bot is vulnerable"""

    def __init__(self, main):
        self.main = main
        self.selected_hatchery = None

    async def should_handle(self):
        """Requirements to build the lair"""
        self.selected_hatchery = self.main.hatcheries.ready.idle
        return (
            not (self.main.lairs or self.main.hives)
            and (
                self.main.base_amount >= 3
                or (self.main.close_enemy_production and len(self.main.evochambers.ready) >= 2)
            )
            and self.main.can_build_unique(LAIR, self.main.caverns, self.selected_hatchery, all_units=True)
        )

    async def handle(self):
        """Finishes the action of making the lair choosing the safest available base"""
        self.main.add_action(self.main.furthest_townhall_to_center(UPGRADETOLAIR_LAIR))
        return True
