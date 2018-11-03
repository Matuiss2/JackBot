"""Everything related to training mutalisks goes here"""
from sc2.constants import HYDRALISK


class TrainHydralisk:
    """Untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        if not local_controller.can_train(HYDRALISK):
            return False
        return local_controller.hydradens.ready

    async def handle(self, iteration):
        """Execute the action of training mutas"""
        local_controller = self.ai
        local_controller.add_action(local_controller.larvae.random.train(HYDRALISK))
        return True