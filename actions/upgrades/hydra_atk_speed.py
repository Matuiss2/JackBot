"""Upgrading zerglings atk speed"""
from sc2.constants import RESEARCH_GROOVEDSPINES, EVOLVEGROOVEDSPINES


class UpgradeGroovedSpines:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        if not local_controller.hydradens.ready.noqueue.idle:
            return False
        return (
            local_controller.can_upgrade(EVOLVEGROOVEDSPINES, RESEARCH_GROOVEDSPINES)
            and not local_controller.floating_buildings_bm
        )

    async def handle(self, iteration):
        """Execute the action of upgrading zergling atk speed"""
        local_controller = self.ai
        den = local_controller.hydradens.noqueue
        local_controller.add_action(den.first(RESEARCH_GROOVEDSPINES))
        return True
