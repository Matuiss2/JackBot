"""Everything related to building logic for the spires goes here"""
from sc2.constants import HYDRALISKDEN


class BuildHydraden:
    """Untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Build the spire if only floating buildings left"""
        local_controller = self.ai
        return (
            local_controller.can_build_uniques(HYDRALISKDEN, local_controller.hydradens)
            and local_controller.lairs
            and not local_controller.close_enemy_production
            and not local_controller.floating_buildings_bm
        )

    async def handle(self, iteration):
        """ Put the spire near the pool"""
        local_controller = self.ai
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(HYDRALISKDEN, position)
            return True
        await local_controller.build(HYDRALISKDEN, near=local_controller.pools.first)
        return True
