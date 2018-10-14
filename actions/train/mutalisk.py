"""Everything related to training mutalisks goes here"""
from sc2.constants import MUTALISK


class TrainMutalisk:
    """Untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        if not self.ai.can_train(MUTALISK):
            return False
        return self.ai.spires.ready

    async def handle(self, iteration):
        """Execute the action of training mutas"""
        self.ai.add_action(self.ai.larvae.random.train(MUTALISK))
        return True
