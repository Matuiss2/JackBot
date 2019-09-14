"""Everything related to building logic for the lairs goes here"""
from sc2.constants import AbilityId, UnitTypeId


class TransformationToLair:
    """Maybe can be improved, probably its a bit greedy it leaves a gap where the bot is vulnerable"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to build the lair"""
        return (
            not self.main.upgraded_base
            and (
                self.main.base_amount >= 3
                or (self.main.close_enemy_production and len(self.main.settled_evochamber) >= 2)
            )
            and self.main.can_build_unique(UnitTypeId.LAIR, self.main.caverns, self.main.hatcheries.ready.idle)
        )

    async def handle(self):
        """Finishes the action of making the lair choosing the safest available base"""
        self.main.add_action(self.main.furthest_townhall_to_center(AbilityId.UPGRADETOLAIR_LAIR))
