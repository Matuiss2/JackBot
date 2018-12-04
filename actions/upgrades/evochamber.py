"""Upgrades made by evolution chambers"""
from sc2.constants import (
    RESEARCH_ZERGGROUNDARMORLEVEL1,
    RESEARCH_ZERGGROUNDARMORLEVEL2,
    RESEARCH_ZERGGROUNDARMORLEVEL3,
    RESEARCH_ZERGMELEEWEAPONSLEVEL1,
    RESEARCH_ZERGMELEEWEAPONSLEVEL2,
    RESEARCH_ZERGMELEEWEAPONSLEVEL3,
    RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
    RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
    RESEARCH_ZERGMISSILEWEAPONSLEVEL3,
)


class UpgradeEvochamber:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_evos = None
        self.upgrade_list = {
            RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            RESEARCH_ZERGGROUNDARMORLEVEL1,
            RESEARCH_ZERGGROUNDARMORLEVEL2,
            RESEARCH_ZERGGROUNDARMORLEVEL3,
            RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
            RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
            RESEARCH_ZERGMISSILEWEAPONSLEVEL3,
        }

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        self.selected_evos = self.ai.evochambers.ready.idle
        return self.selected_evos

    async def handle(self, iteration):
        """Execute the action of upgrading armor, melee and ranged attacks"""
        local_controller = self.ai
        for evo in self.selected_evos:
            upgrades = await local_controller.get_available_abilities(evo)
            for upgrade in upgrades:
                if upgrade in self.upgrade_list and local_controller.can_afford(upgrade):
                    if upgrade in (
                        RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
                        RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
                        RESEARCH_ZERGMISSILEWEAPONSLEVEL3,
                    ):
                        if local_controller.hydradens:
                            local_controller.add_action(evo(upgrade))
                            return True
                    else:
                        local_controller.add_action(evo(upgrade))
                        return True
        return True
