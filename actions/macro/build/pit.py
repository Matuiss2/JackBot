"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import INFESTATIONPIT


class BuildPit:
    """Can be improved so its more situational and less greedy"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirement to build the infestation pit, sometimes it creates a big gap on the bot,
        maybe we should raise the lock"""
        return self.main.base_amount > 4 and self.main.can_build_unique(INFESTATIONPIT, self.main.pits)

    async def handle(self):
        """Places the pit"""
        build = await self.main.place_building(INFESTATIONPIT)
        if not build:
            return False
        return True
