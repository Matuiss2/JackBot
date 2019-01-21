"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import INFESTATIONPIT


class BuildPit:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Builds the infestation pit, placement fails on very limited situations"""
        local_controller = self.controller
        return (
            len(local_controller.townhalls) > 4
            and local_controller.time > 690
            and local_controller.can_build_unique(INFESTATIONPIT, local_controller.pits)
        )

    async def handle(self):
        """Build it behind the mineral line if there is space"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if not position:
            print("wanted position unavailable for pit")
            return False
        selected_drone = local_controller.select_build_worker(position)
        local_controller.add_action(selected_drone.build(INFESTATIONPIT, position))
        return True
