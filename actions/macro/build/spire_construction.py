"""Everything related to building logic for the spires goes here"""
from sc2.constants import UnitTypeId


class SpireConstruction:
    """Untested"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Build the spire if only floating buildings left"""
        return (
            self.main.can_build_unique(UnitTypeId.SPIRE, self.main.spires)
            and self.main.floated_buildings_bm
            and self.main.upgraded_bases
        )

    async def handle(self):
        """Places the spire"""
        await self.main.place_building(UnitTypeId.SPIRE)
