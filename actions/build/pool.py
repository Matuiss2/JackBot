"""Everything related to building logic for the pools goes here"""
from sc2.constants import SPAWNINGPOOL


class BuildPool:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Should this action be handled"""
        local_controller = self.ai
        return (
            not local_controller.already_pending(SPAWNINGPOOL)
            and not local_controller.pools
            and local_controller.can_afford(SPAWNINGPOOL)
            and (
                len(local_controller.townhalls) >= 2
                or (local_controller.close_enemy_production and local_controller.time < 300)
            )
        )

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.ai
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(SPAWNINGPOOL, position)
            return True

        await local_controller.build(SPAWNINGPOOL, near=self.find_position())
        return True

    def find_position(self):
        """Previous placement"""
        local_controller = self.ai
        map_center = local_controller.game_info.map_center
        return local_controller.townhalls.furthest_to(map_center).position.towards_with_random_angle(map_center, -10)
