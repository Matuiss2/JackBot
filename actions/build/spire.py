"""Everything related to building logic for the spires goes here"""
from sc2.constants import SPIRE


class BuildSpire:
    """Untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Build the spire if only floating buildings left"""
        local_controller = self.ai
        return (
            local_controller.can_build_unique(SPIRE, local_controller.spires)
            and local_controller.floating_buildings_bm
            and (local_controller.lairs or local_controller.hives)
        )

    async def handle(self, iteration):
        """ Put the spire near the pool"""
        local_controller = self.ai
        await local_controller.build(SPIRE, near=local_controller.pools.first)
        return True
