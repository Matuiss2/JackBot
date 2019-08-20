"""Everything related to training ultralisks goes here"""
from sc2.constants import UnitTypeId, UpgradeId


class UltraliskCreation:
    """Good for now but it might need to be changed vs particular enemy units compositions"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirement for training ultralisks"""
        if not self.main.can_train(UnitTypeId.ULTRALISK, self.main.settled_cavern):
            return False
        if self.main.second_armor and not self.main.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL3):
            self.main.armor_three_lock = True
            return False
        self.main.armor_three_lock = False
        return True

    async def handle(self):
        """Execute the action of training ultralisks"""
        self.main.add_action(self.main.larvae.random.train(UnitTypeId.ULTRALISK))
