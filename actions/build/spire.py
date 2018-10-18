"""Everything related to building logic for the spires goes here"""
from sc2.constants import SPIRE


class BuildSpire:
    """Untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Build the spire if only floating buildings left"""
        return (
            not self.ai.spires
            and self.ai.can_afford(SPIRE)
            and self.ai.floating_buildings_bm
            and not self.ai.already_pending(SPIRE)
            and (self.ai.lairs or self.ai.hives)
        )

    async def handle(self, iteration):
        """ Put the spire near the pool"""
        await self.ai.build(SPIRE, near=self.ai.pools.first)
        return True
