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
        return self.ai.evochambers.ready.idle

    async def handle(self, iteration):
        """Execute the action of upgrading armor and melee attacks"""
        local_controller = self.ai
        for evo in local_controller.evochambers.idle:
            upgrades = await local_controller.get_available_abilities(evo)
            for upgrade in upgrades:
                if upgrade in self.upgrade_list and local_controller.can_afford(upgrade):
                    local_controller.add_action(evo(upgrade))
                    return True
        return True
