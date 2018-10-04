"""Everything related to upgrades logic goes here"""
from sc2.constants import (
    CHITINOUSPLATING,
    EVOLUTIONCHAMBER,
    HATCHERY,
    OVERLORDSPEED,
    RESEARCH_CHITINOUSPLATING,
    RESEARCH_PNEUMATIZEDCARAPACE,
    RESEARCH_ZERGLINGADRENALGLANDS,
    RESEARCH_ZERGMELEEWEAPONSLEVEL1,
    RESEARCH_ZERGMELEEWEAPONSLEVEL2,
    RESEARCH_ZERGMELEEWEAPONSLEVEL3,
    RESEARCH_ZERGLINGMETABOLICBOOST,
    RESEARCH_ZERGGROUNDARMORLEVEL1,
    RESEARCH_ZERGGROUNDARMORLEVEL2,
    RESEARCH_ZERGGROUNDARMORLEVEL3,
    SPAWNINGPOOL,
    ULTRALISKCAVERN,
    ZERGLINGATTACKSPEED,
    ZERGMELEEWEAPONSLEVEL1,
    ZERGMELEEWEAPONSLEVEL2,
    ZERGMELEEWEAPONSLEVEL3,
    ZERGLINGMOVEMENTSPEED,
    ZERGGROUNDARMORSLEVEL1,
    ZERGGROUNDARMORSLEVEL2,
    ZERGGROUNDARMORSLEVEL3,
)


class upgrades_control:
    async def evochamber_upgrades(self):
        """Can be rewritten so it doesnt need the list,
        if the evochamber gets destroyed while upgrading it will never try again, can be improved """
        evochamber = self.units(EVOLUTIONCHAMBER).ready
        if evochamber.idle:
            for evo in evochamber.idle:
                if not self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL1) and self.can_afford(ZERGGROUNDARMORSLEVEL1):
                    self.actions.append(evo(RESEARCH_ZERGGROUNDARMORLEVEL1))
                    break
                if not self.already_pending_upgrade(ZERGMELEEWEAPONSLEVEL1) and self.can_afford(ZERGMELEEWEAPONSLEVEL1):
                    self.actions.append(evo(RESEARCH_ZERGMELEEWEAPONSLEVEL1))
                    break
                if not self.already_pending_upgrade(ZERGMELEEWEAPONSLEVEL2) and self.can_afford(ZERGMELEEWEAPONSLEVEL2):
                    self.actions.append(evo(RESEARCH_ZERGMELEEWEAPONSLEVEL2))
                    break
                if not self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL2) and self.can_afford(ZERGGROUNDARMORSLEVEL2):
                    self.actions.append(evo(RESEARCH_ZERGGROUNDARMORLEVEL2))
                    break
                if not self.already_pending_upgrade(ZERGMELEEWEAPONSLEVEL3) and self.can_afford(ZERGMELEEWEAPONSLEVEL3):
                    self.actions.append(evo(RESEARCH_ZERGMELEEWEAPONSLEVEL3))
                    break
                if not self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL3) and self.can_afford(ZERGGROUNDARMORSLEVEL3):
                    self.actions.append(evo(RESEARCH_ZERGGROUNDARMORLEVEL3))
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
        await self.evochamber_upgrades()
        self.hatchery_cavern_upgrades()
        self.pool_upgrades()
