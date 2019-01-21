"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import INFESTATIONPIT


class BuildPit:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Builds the infestation pit, placement fails on very limited situations"""
        local_controller = self.controller
        return (
            len(local_controller.townhalls) > 4
            and local_controller.time > 600
            and local_controller.can_build_unique(INFESTATIONPIT, local_controller.pits)
        )

    async def handle(self):
        """Build the pit"""
        build = await self.controller.place_building(INFESTATIONPIT)
        if not build:
            return False
        return True
