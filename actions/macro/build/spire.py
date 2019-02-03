"""Everything related to building logic for the spires goes here"""
from sc2.constants import SPIRE


class BuildSpire:
    """Untested"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Build the spire if only floating buildings left"""
        return (
            self.controller.can_build_unique(SPIRE, self.controller.spires)
            and self.controller.floating_buildings_bm
            and (self.controller.lairs or self.controller.hives)
        )

    async def handle(self):
        """Places the spire"""
        build = await self.controller.place_building(SPIRE)
        if not build:
            return False
        return True
