from sc2.constants import BURROW, RESEARCH_BURROW


class UpgradeBurrow:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return (
            self.ai.lairs
            and self.ai.hatcheries
            and not self.ai.already_pending_upgrade(BURROW)
            and self.ai.can_afford(RESEARCH_BURROW)
        )

    async def handle(self, iteration):
        chosen_base = self.ai.hatcheries.idle.closest_to(self.ai._game_info.map_center)
        self.ai.actions.append(chosen_base(RESEARCH_BURROW))
        return True
