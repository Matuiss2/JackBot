"""Everything related to building logic for the hydralisk den goes here"""
from sc2.constants import HYDRALISKDEN


class BuildHydraden:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_pools = None

    async def should_handle(self):
        """Build the hydraden"""
        local_controller = self.controller
        self.selected_pools = local_controller.pools
        return (
            local_controller.can_build_unique(
                HYDRALISKDEN, local_controller.hydradens, (local_controller.lairs and self.selected_pools)
            )
            and not local_controller.close_enemy_production
            and not local_controller.floating_buildings_bm
            and len(local_controller.townhalls) >= 3
            and not local_controller.ground_enemies.closer_than(20, self.selected_pools.first)
        )

    async def handle(self):
        """Build it behind the mineral line if there is space, if not places it near a pool"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if not position:
            print("wanted position not found for hydraden")
            return False
        selected_drone = local_controller.select_build_worker(position)
        local_controller.add_action(selected_drone.build(HYDRALISKDEN, position))
        return True
