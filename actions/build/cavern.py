"""Everything related to building logic for the ultra cavern goes here"""
from sc2.constants import ULTRALISKCAVERN, ZERGGROUNDARMORSLEVEL3


class BuildCavern:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Builds the ultralisk cavern, placement can maybe be improved(far from priority)"""
        local_controller = self.controller
        return local_controller.can_build_unique(ULTRALISKCAVERN, local_controller.caverns, local_controller.hives)

    async def handle(self):
        """Build the cavern"""
        build = await self.controller.place_building(ULTRALISKCAVERN)
        if not build:
            return False
        return True
