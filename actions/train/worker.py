from sc2.constants import (DRONE, LARVA)

class TrainWorker:

    def __init__(self, ai):
        self.ai = ai

    def should_handle(self, iteration):
        """Should this action be handled"""
        return (
            len(self.ai.units(LARVA)) > 0
            and len(self.ai.workers) < 65
            and self.ai.can_afford(DRONE)
            and self.ai.can_feed(DRONE)
        )

    async def handle(self, iteration):
        larva = self.ai.units(LARVA)
        self.ai.actions.append(larva.random.train(DRONE))
