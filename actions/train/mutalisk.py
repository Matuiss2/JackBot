"""Everything related to training mutalisks goes here"""
from sc2.constants import MUTALISK


class TrainMutalisk:
    """Untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return local_controller.spires.ready and local_controller.can_train(MUTALISK)

    async def handle(self, iteration):
        """Execute the action of training mutas"""
        local_controller = self.ai
        local_controller.add_action(local_controller.larvae.random.train(MUTALISK))
        return True
