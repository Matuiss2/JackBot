from sc2.constants import SPAWNINGPOOL


class BuildPool:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Should this action be handled"""
        return (
            not self.ai.already_pending(SPAWNINGPOOL)
            and not self.ai.pools
            and self.ai.can_afford(SPAWNINGPOOL)
            and (len(self.ai.townhalls) >= 2 or (self.ai.close_enemy_production and self.ai.time < 300))
        )

    async def handle(self, iteration):
        position = await self.ai.get_production_position()
        if position:
            await self.ai.build(SPAWNINGPOOL, position)
            return True
        else:
            await self.ai.build(SPAWNINGPOOL, near=self.find_position())
            return True

    def find_position(self):
        return self.ai.townhalls.furthest_to(self.ai.game_info.map_center).position.towards_with_random_angle(
            self.ai.game_info.map_center, -10
        )
