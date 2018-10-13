from sc2.constants import MUTALISK


class TrainMutalisk:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        if not self.ai.can_train(MUTALISK):
            return False
        return self.ai.spires.ready

    async def handle(self, iteration):
        self.ai.actions.append(self.ai.larvae.random.train(MUTALISK))
        return True
