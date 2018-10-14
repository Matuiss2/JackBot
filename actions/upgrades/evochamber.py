"""Upgrades made by evolution chambers"""
from sc2.constants import (
    RESEARCH_ZERGGROUNDARMORLEVEL1,
    RESEARCH_ZERGGROUNDARMORLEVEL2,
    RESEARCH_ZERGGROUNDARMORLEVEL3,
    RESEARCH_ZERGMELEEWEAPONSLEVEL1,
    RESEARCH_ZERGMELEEWEAPONSLEVEL2,
    RESEARCH_ZERGMELEEWEAPONSLEVEL3,
)


class UpgradeEvochamber:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.upgrade_list = [
            RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            RESEARCH_ZERGGROUNDARMORLEVEL1,
            RESEARCH_ZERGGROUNDARMORLEVEL2,
            RESEARCH_ZERGGROUNDARMORLEVEL3,
        ]

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return self.ai.evochambers.ready.idle

    async def handle(self, iteration):
        """Execute the action of upgrading armor and melee attacks"""
        for evo in self.ai.evochambers.idle:
            upgrades = await self.ai.get_available_abilities(evo)
            for upgrade in upgrades:
                if upgrade in self.upgrade_list and self.ai.can_afford(upgrade):
                    self.ai.add_action(evo(upgrade))
                    return True
        return True
