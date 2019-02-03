"""Upgrading hydras speed and range"""
from sc2.constants import EVOLVEGROOVEDSPINES, EVOLVEMUSCULARAUGMENTS, RESEARCH_GROOVEDSPINES, RESEARCH_MUSCULARAUGMENTS


class UpgradesFromHydraden:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_dens = self.selected_research = None

    async def should_handle(self):
        """Requirements to upgrade stuff from hydradens"""
        self.selected_dens = self.controller.hydradens.ready.noqueue.idle
        if self.controller.floating_buildings_bm:
            return False
        if self.controller.can_upgrade(EVOLVEGROOVEDSPINES, RESEARCH_GROOVEDSPINES, self.selected_dens):
            self.selected_research = RESEARCH_GROOVEDSPINES
            return True
        if (
            self.controller.can_upgrade(EVOLVEMUSCULARAUGMENTS, RESEARCH_MUSCULARAUGMENTS, self.selected_dens)
            and self.controller.already_pending_upgrade(EVOLVEGROOVEDSPINES) == 1
        ):
            self.selected_research = RESEARCH_MUSCULARAUGMENTS
            return True

    async def handle(self):
        """Execute the action of upgrading hydras speed and range"""
        self.controller.add_action(self.selected_dens.first(self.selected_research))
        return True
