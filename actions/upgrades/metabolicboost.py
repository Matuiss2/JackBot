from sc2.constants import RESEARCH_ZERGLINGMETABOLICBOOST, SPAWNINGPOOL, ZERGLINGMOVEMENTSPEED


class UpgradeMetabolicBoost:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        if not self.ai.pools.ready.idle:
            return False

        return not self.ai.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) and self.ai.can_afford(
            RESEARCH_ZERGLINGMETABOLICBOOST
        )

    async def handle(self, iteration):
        pool = self.ai.pools.ready
        self.ai.actions.append(pool.first(RESEARCH_ZERGLINGMETABOLICBOOST))
        return True
