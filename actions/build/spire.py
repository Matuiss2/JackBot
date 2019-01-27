"""Everything related to building logic for the spires goes here"""
from sc2.constants import SPIRE


class BuildSpire:
    """Untested"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Build the spire if only floating buildings left"""
        local_controller = self.controller
        return (
            local_controller.can_build_unique(SPIRE, local_controller.spires)
            and local_controller.floating_buildings_bm
            and (local_controller.lairs or local_controller.hives)
        )

    async def handle(self):
        """Places the spire"""
        build = await self.controller.place_building(SPIRE)
        if not build:
            return False
        return True
