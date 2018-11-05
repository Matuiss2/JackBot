"""Everything related to building logic for the ultra cavern goes here"""
from sc2.constants import ULTRALISKCAVERN


class BuildCavern:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the ultralisk cavern, placement can maybe be improved(far from priority)"""
        local_controller = self.ai
        return (
            local_controller.evochambers
            and local_controller.hives
            and local_controller.can_build_uniques(ULTRALISKCAVERN, local_controller.caverns)
        )

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not build between the main and natural"""
        local_controller = self.ai
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(ULTRALISKCAVERN, position)
            return True
        await local_controller.build(
            ULTRALISKCAVERN,
            near=local_controller.townhalls.furthest_to(local_controller.game_info.map_center).position.towards(
                local_controller.main_base_ramp.depot_in_middle, 6
            ),
        )
        return True
