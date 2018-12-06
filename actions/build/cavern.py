"""Everything related to building logic for the ultra cavern goes here"""
from sc2.constants import ULTRALISKCAVERN


class BuildCavern:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the ultralisk cavern, placement can maybe be improved(far from priority)"""
        local_controller = self.ai
        return local_controller.can_build_unique(ULTRALISKCAVERN, local_controller.caverns, local_controller.hives)

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not build between the main and natural"""
        local_controller = self.ai
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(ULTRALISKCAVERN, position)
            return True
        if local_controller.furthest_townhall_to_map_center:
            await local_controller.build(ULTRALISKCAVERN, near=self.hardcoded_position())
            return True

    def hardcoded_position(self):
        """Previous placement"""
        local_controller = self.ai
        return local_controller.furthest_townhall_to_map_center.towards(
            local_controller.main_base_ramp.depot_in_middle, 6
        )
