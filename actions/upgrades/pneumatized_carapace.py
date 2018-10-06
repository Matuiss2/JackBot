from sc2.constants import (
    OVERLORDSPEED,
    RESEARCH_PNEUMATIZEDCARAPACE
)

class UpgradeChitinousPlating:

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return (
            self.ai.caverns
            and self.ai.hatcheries
            and not self.ai.already_pending_upgrade(OVERLORDSPEED)
            and self.ai.can_afford(RESEARCH_PNEUMATIZEDCARAPACE)
        )

    async def handle(self, iteration):
        chosen_base = self.ai.hatcheries.closest_to(self.ai._game_info.map_center)
        self.ai.actions.append(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))
        return True
