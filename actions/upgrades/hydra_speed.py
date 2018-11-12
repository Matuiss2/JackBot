"""Upgrading hydras speed"""
from sc2.constants import RESEARCH_MUSCULARAUGMENTS, EVOLVEMUSCULARAUGMENTS, EVOLVEGROOVEDSPINES


class UpgradeMuscularAugments:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            local_controller.hydradens.ready.noqueue.idle
            and local_controller.can_upgrade(EVOLVEMUSCULARAUGMENTS, RESEARCH_MUSCULARAUGMENTS)
            and not local_controller.floating_buildings_bm
            and local_controller.already_pending_upgrade(EVOLVEGROOVEDSPINES) == 1
        )

    async def handle(self, iteration):
        """Execute the action of upgrading hydras speed"""
        local_controller = self.ai
        den = local_controller.hydradens.noqueue
        local_controller.add_action(den.first(RESEARCH_MUSCULARAUGMENTS))
        return True
