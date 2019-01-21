"""Everything related to building logic for the ultra cavern goes here"""
from sc2.constants import ULTRALISKCAVERN


class BuildCavern:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Builds the ultralisk cavern, placement can maybe be improved(far from priority)"""
        local_controller = self.controller
        return local_controller.can_build_unique(ULTRALISKCAVERN, local_controller.caverns, local_controller.hives)

    async def handle(self):
        """Build it behind the mineral line if there is space"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if not position:
            print("wanted position unavailable for cavern")
            return False
        selected_drone = local_controller.select_build_worker(position)
        local_controller.add_action(selected_drone.build(ULTRALISKCAVERN, position))
        return True
