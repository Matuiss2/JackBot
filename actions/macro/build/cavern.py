"""Everything related to building logic for the ultralisk cavern goes here"""
from sc2.constants import ULTRALISKCAVERN


class BuildCavern:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Builds the ultralisk cavern"""
        return self.controller.can_build_unique(ULTRALISKCAVERN, self.controller.caverns, self.controller.hives)

    async def handle(self):
        """Build the cavern on the decided placement"""
        build = await self.controller.place_building(ULTRALISKCAVERN)
        if not build:
            return False
        return True
