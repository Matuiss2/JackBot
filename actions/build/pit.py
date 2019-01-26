"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import INFESTATIONPIT


class BuildPit:
    """Can be improved so its more situational and less greedy"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirement to build the infestation pit, sometimes it creates a big gap on the bot,
        maybe we should raise the lock"""
        local_controller = self.controller
        return (
            len(local_controller.townhalls) > 4
            and local_controller.can_build_unique(INFESTATIONPIT, local_controller.pits)
        )

    async def handle(self):
        """Places the pit"""
        build = await self.controller.place_building(INFESTATIONPIT)
        if not build:
            return False
        return True
