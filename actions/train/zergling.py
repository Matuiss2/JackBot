"""Everything related to training zergling goes here"""
from sc2.constants import ZERGLING, ZERGLINGMOVEMENTSPEED


class TrainZergling:
    """Ok for now, mutas ratio untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """good enough for now"""
        if (
            not self.ai.pools.ready
            and 170 <= self.ai.time <= 230
            and not self.ai.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
            and not self.ai.close_enemy_production
        ):
            return False

        if not self.ai.can_train(ZERGLING):
            return False

        if self.ai.caverns.ready and self.ai.time < 1380:
            if not len(self.ai.ultralisks) * 8.5 > len(self.ai.zerglings):
                return False

        if self.ai.floating_buildings_bm:
            if self.ai.supply_used > 150:
                return False
            if not len(self.ai.mutalisks) * 10 > len(self.ai.zerglings):
                return False
        return True

    async def handle(self, iteration):
        """Execute the action of training zerglings"""
        self.ai.add_action(self.ai.larvae.random.train(ZERGLING))
        return True
