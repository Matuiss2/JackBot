"""Everything related to upgrades logic goes here"""
from sc2.constants import (
    CHITINOUSPLATING,
    EVOLUTIONCHAMBER,
    HATCHERY,
    OVERLORDSPEED,
    RESEARCH_CHITINOUSPLATING,
    RESEARCH_PNEUMATIZEDCARAPACE,
    RESEARCH_ZERGGROUNDARMORLEVEL1,
    RESEARCH_ZERGGROUNDARMORLEVEL2,
    RESEARCH_ZERGGROUNDARMORLEVEL3,
    RESEARCH_ZERGLINGADRENALGLANDS,
    RESEARCH_ZERGLINGMETABOLICBOOST,
    RESEARCH_ZERGMELEEWEAPONSLEVEL1,
    RESEARCH_ZERGMELEEWEAPONSLEVEL2,
    RESEARCH_ZERGMELEEWEAPONSLEVEL3,
    SPAWNINGPOOL,
    ULTRALISKCAVERN,
    ZERGLINGATTACKSPEED,
    ZERGLINGMOVEMENTSPEED,
)


class UpgradesControl:
    """Group every upgrade dividing it by the structure that host it"""

    async def evochamber_upgrades(self):
        """Can be rewritten so it doesnt need the list,
        if the evochamber gets destroyed while upgrading it will never try again, can be improved """
        upgrade_list = [
            RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            RESEARCH_ZERGGROUNDARMORLEVEL1,
            RESEARCH_ZERGGROUNDARMORLEVEL2,
            RESEARCH_ZERGGROUNDARMORLEVEL3,
        ]
        evochamber = self.units(EVOLUTIONCHAMBER).ready
        if evochamber.idle:
            for evo in evochamber.idle:
                upgrades = await self.get_available_abilities(evo)
                for upgrade in upgrades:
                    if upgrade in upgrade_list and self.can_afford(upgrade):
                        self.actions.append(evo(upgrade))
                        break

    def hatchery_cavern_upgrades(self):
        """Burrow is missing, find the right timing for it"""
        cavern = self.units(ULTRALISKCAVERN).ready
        if cavern:
            if not self.already_pending_upgrade(CHITINOUSPLATING) and self.can_afford(CHITINOUSPLATING):
                self.actions.append(cavern.idle.first(RESEARCH_CHITINOUSPLATING))
            if self.units(HATCHERY):
                if not self.already_pending_upgrade(OVERLORDSPEED) and self.can_afford(RESEARCH_PNEUMATIZEDCARAPACE):
                    chosen_base = self.units(HATCHERY).closest_to(self._game_info.map_center)
                    self.actions.append(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))
                # if not self.already_pending_upgrade(BURROW) and self.can_afford(RESEARCH_BURROW):
                #     chosen_base = self.units(HATCHERY).random
                #     self.actions.append(chosen_base(RESEARCH_BURROW))

    def pool_upgrades(self):
        """Good for now"""
        pool = self.units(SPAWNINGPOOL).ready
        if pool.idle:
            if not self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) or not self.already_pending_upgrade(
                ZERGLINGATTACKSPEED
            ):
                if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST):
                    self.actions.append(pool.first(RESEARCH_ZERGLINGMETABOLICBOOST))
                if self.can_afford(RESEARCH_ZERGLINGADRENALGLANDS):
                    self.actions.append(pool.first(RESEARCH_ZERGLINGADRENALGLANDS))

    async def all_upgrades(self):
        """Execute all upgrade functions"""
        await self.evochamber_upgrades()
        self.hatchery_cavern_upgrades()
        self.pool_upgrades()
