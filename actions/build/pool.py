"""Everything related to building logic for the pools goes here"""
from sc2.constants import SPAWNINGPOOL


class BuildPool:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Should this action be handled"""
        local_controller = self.controller
        return local_controller.can_build_unique(SPAWNINGPOOL, local_controller.pools) and (
            len(local_controller.townhalls) >= 2
            or local_controller.close_enemy_production
            or local_controller.time > 145
        )

    async def handle(self):
        """Build it behind the mineral line if there is space"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if not position:
            print("wanted position unavailable for pool")
            return False
        selected_drone = local_controller.select_build_worker(position)
        local_controller.add_action(selected_drone.build(SPAWNINGPOOL, position))
        return True
