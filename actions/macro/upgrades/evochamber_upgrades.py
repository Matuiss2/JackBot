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


class UpgradesFromEvochamber:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.upgrades_added = False
        self.upgrade_list = [
            RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            RESEARCH_ZERGGROUNDARMORLEVEL1,
            RESEARCH_ZERGGROUNDARMORLEVEL2,
            RESEARCH_ZERGGROUNDARMORLEVEL3,
        ]
        self.ranged_upgrades = {
            RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
            RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
            RESEARCH_ZERGMISSILEWEAPONSLEVEL3,
        }

    async def should_handle(self):
        """Requirements to upgrade stuff from evochambers"""
        return self.main.evochambers.ready.idle

    async def handle(self):
        """Execute the action of upgrading armor, melee and ranged attacks"""
        if self.main.hydradens and not self.upgrades_added:
            self.upgrades_added = True
            self.upgrade_list.extend(self.ranged_upgrades)
        for evo in self.main.evochambers.ready.idle:
            for upgrade in await self.main.get_available_abilities(evo):
                if upgrade in self.upgrade_list and self.main.can_afford(upgrade):
                    self.main.add_action(evo(upgrade))
                    return True
        return True
