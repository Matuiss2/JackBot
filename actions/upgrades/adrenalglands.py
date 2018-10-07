from sc2.constants import RESEARCH_ZERGLINGADRENALGLANDS, ZERGLINGATTACKSPEED


class UpgradeAdrenalGlands:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        if not self.ai.pools.ready.idle:
            return False

        return (
            not self.ai.already_pending_upgrade(ZERGLINGATTACKSPEED)
            and self.ai.hives
            and self.ai.can_afford(RESEARCH_ZERGLINGADRENALGLANDS)
        )

    async def handle(self, iteration):
        pool = self.ai.pools.ready
        self.ai.actions.append(pool.first(RESEARCH_ZERGLINGADRENALGLANDS))
        return True
