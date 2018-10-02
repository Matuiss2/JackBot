from sc2.constants import (
    CHITINOUSPLATING,
    EVOLUTIONCHAMBER,
    HATCHERY,
    OVERLORDSPEED,
    RESEARCH_CHITINOUSPLATING,
    RESEARCH_PNEUMATIZEDCARAPACE,
    RESEARCH_ZERGLINGADRENALGLANDS,
    RESEARCH_ZERGLINGMETABOLICBOOST,
    SPAWNINGPOOL,
    ULTRALISKCAVERN,
    ZERGLINGATTACKSPEED,
    ZERGLINGMOVEMENTSPEED,
)


class upgrades_control:
    async def evochamber_upgrades(self):
        evochamber = self.units(EVOLUTIONCHAMBER).ready
        if self.abilities_list and evochamber.idle:
            for evo in evochamber.idle:
                abilities = await self.get_available_abilities(evo)
                for ability in self.abilities_list:
                    if ability in abilities:
                        if self.can_afford(ability):
                            self.actions.append(evo(ability))
                            self.abilities_list.remove(ability)
                            break

    def hatchery_cavern_upgrades(self):
        cavern = self.units(ULTRALISKCAVERN).ready
        if cavern:
            if not self.already_pending_upgrade(CHITINOUSPLATING) and self.can_afford(CHITINOUSPLATING):
                self.actions.append(cavern.idle.first(RESEARCH_CHITINOUSPLATING))
            if self.units(HATCHERY):
                if not self.already_pending_upgrade(OVERLORDSPEED) and self.can_afford(RESEARCH_PNEUMATIZEDCARAPACE):
                    chosen_base = self.units(HATCHERY).random
                    self.actions.append(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))
                # if not self.already_pending_upgrade(BURROW) and self.can_afford(RESEARCH_BURROW):
                #     chosen_base = self.units(HATCHERY).random
                #     self.actions.append(chosen_base(RESEARCH_BURROW))

    def pool_upgrades(self):
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
