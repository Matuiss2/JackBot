"""Everything related to building logic for the ultralisk cavern goes here"""
from sc2.constants import UnitTypeId


class CavernConstruction:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Builds the ultralisk cavern"""
        return self.main.can_build_unique(UnitTypeId.ULTRALISKCAVERN, self.main.caverns, self.main.hives)

    async def handle(self):
        """Build the cavern on the decided placement"""
        await self.main.place_building(UnitTypeId.ULTRALISKCAVERN)
