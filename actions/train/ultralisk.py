"""Everything related to training ultralisks goes here"""
from sc2.constants import ULTRALISK, ZERGGROUNDARMORSLEVEL3


class TrainUltralisk:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Good for now but it might need to be changed vs particular
         enemy units compositions"""
        if not self.ai.caverns.ready:
            return False

        if not self.ai.already_pending_upgrade(ZERGGROUNDARMORSLEVEL3) and self.ai.time > 780:
            return False

        if not self.ai.can_train(ULTRALISK):
            return False

        return True

    async def handle(self, iteration):
        """Execute the action of training ultralisks"""
        self.ai.adding(self.ai.larvae.random.train(ULTRALISK))
        return True
