from sc2.constants import (
    CHITINOUSPLATING,
    RESEARCH_CHITINOUSPLATING
)

class UpgradeChitinousPlating:

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return (
            self.ai.caverns
            and not self.already_pending_upgrade(CHITINOUSPLATING)
            and self.can_afford(CHITINOUSPLATING)
        )

    async def handle(self, iteration):
        self.ai.actions.append(self.ai.caverns.idle.first(RESEARCH_CHITINOUSPLATING))
        return True
