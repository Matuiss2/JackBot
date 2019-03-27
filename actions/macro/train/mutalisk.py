"""Everything related to training mutalisks goes here"""
from sc2.constants import MUTALISK


class TrainMutalisk:
    """Untested"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to train mutalisks, maybe some locks are needed"""
        return self.main.can_train(MUTALISK, self.main.spires.ready)

    async def handle(self):
        """Execute the action of training mutas"""
        self.main.add_action(self.main.larvae.random.train(MUTALISK))
