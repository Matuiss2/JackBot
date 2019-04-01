"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import UnitTypeId


class BuildPit:
    """Can be improved so its more situational and less greedy"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirement to build the infestation pit, sometimes it creates a big gap on the bot,
        maybe we should raise the lock"""
        return self.main.base_amount > 4 and self.main.can_build_unique(UnitTypeId.INFESTATIONPIT, self.main.pits)

    async def handle(self):
        """Places the pit"""
        await self.main.place_building(UnitTypeId.INFESTATIONPIT)
