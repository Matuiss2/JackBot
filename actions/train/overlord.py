from sc2.constants import (OVERLORD, LARVA)

class TrainOverlord:

    def __init__(self, ai):
        self.ai = ai

    def should_handle(self, iteration):
        """Should this action be handled"""
        return (
            # not self.ai.supply_cap >= 200
            len(self.ai.units(LARVA)) > 0
            and self.ai.supply_left < 8
            and self.ai.can_afford(OVERLORD)
            # and (
            #     (len(self.townhalls) in (1, 2) and self.already_pending(OVERLORD))
            #     or self.ai.already_pending(OVERLORD) >= 2
            # )
        )

    async def handle(self, iteration):
        self.ai.actions.append(self.ai.units(LARVA).random.train(OVERLORD))
        return True
