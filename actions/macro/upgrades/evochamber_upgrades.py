"""Upgrades made by evolution chambers"""
from sc2.constants import AbilityId


class UpgradesFromEvochamber:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.upgrades_added = False
        self.upgrade_list = [
            AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1,
            AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2,
            AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3,
        ]
        self.ranged_upgrades = {
            AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
            AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
            AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3,
        }

    async def should_handle(self):
        """Requirements to upgrade stuff from evochambers"""
        return self.main.evochambers.ready

    async def handle(self):
        """Execute the action of upgrading armor, melee and ranged attacks"""
        if self.main.hydradens and not self.upgrades_added:
            self.upgrades_added = True
            self.upgrade_list.extend(self.ranged_upgrades)
        for evo in self.main.evochambers.ready.prefer_idle:
            for upgrade in await self.main.get_available_abilities(evo):
                if upgrade in self.upgrade_list and self.main.can_afford(upgrade):
                    self.main.add_action(evo(upgrade))
