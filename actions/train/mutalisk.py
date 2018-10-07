from sc2.constants import MUTALISK


class TrainMutalisk:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return self.ai.spires.ready and self.ai.can_afford(MUTALISK) and self.ai.can_feed(MUTALISK)

    async def handle(self, iteration):
        self.ai.actions.append(self.ai.larvae.random.train(MUTALISK))
        return True
