"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Builds the evolution chambers"""
        local_controller = self.controller
        return (
            local_controller.building_requirement(EVOLUTIONCHAMBER, local_controller.pools.ready)
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.spines.ready) >= 4)
            )
            and len(local_controller.evochambers) + local_controller.already_pending(EVOLUTIONCHAMBER) < 2
            and local_controller.drones
        )

    async def handle(self):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if not position and local_controller.townhalls:
            print("wanted position not found for evo")
            return False
        selected_drone = local_controller.select_build_worker(position)
        self.controller.add_action(selected_drone.build(EVOLUTIONCHAMBER, position))
        return True
