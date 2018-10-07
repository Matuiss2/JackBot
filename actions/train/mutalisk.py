from sc2.constants import (MUTALISK)

class TrainMutalisk:

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return (
            self.spires.ready
            and self.can_afford(MUTALISK) and self.can_feed(MUTALISK)
        )

    async def handle(self, iteration):
        self.actions.append(self.larvae.random.train(MUTALISK))
        return True
