from sc2.constants import ULTRALISKCAVERN, ZERGLING, ZERGLINGMOVEMENTSPEED


class TrainZergling:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """good enough for now"""

        if not self.ai.pools.ready:
            return False

        if (
            170 <= self.ai.time <= 230
            and not self.ai.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
            and not self.ai.close_enemy_production
        ):
            return False

        if not self.ai.can_train(ZERGLING):
            return False

        if self.ai.units(ULTRALISKCAVERN).ready and self.ai.time < 1380:
            if not len(self.ai.ultralisks) * 8.5 > len(self.ai.zerglings):
                return False
        return True

    async def handle(self, iteration):
        self.ai.actions.append(self.ai.larvae.random.train(ZERGLING))
        return True
