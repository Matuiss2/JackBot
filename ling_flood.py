"""SC2 zerg bot by Matuiss, Thommath and Tweakimp"""
import sc2
from sc2 import Difficulty, Race, maps, run_game
from sc2.constants import (
    CANCEL,
    CANCEL_MORPHHIVE,
    CANCEL_MORPHLAIR,
    CANCEL_MORPHOVERSEER,
    DRONE,
    EFFECT_INJECTLARVA,
    HATCHERY,
    HIVE,
    INFESTATIONPIT,
    LAIR,
    LARVA,
    MORPH_OVERSEER,
    OVERLORD,
    OVERLORDCOCOON,
    OVERSEER,
    PROBE,
    QUEEN,
    QUEENSPAWNLARVATIMER,
    RESEARCH_ZERGGROUNDARMORLEVEL1,
    RESEARCH_ZERGGROUNDARMORLEVEL2,
    RESEARCH_ZERGGROUNDARMORLEVEL3,
    RESEARCH_ZERGMELEEWEAPONSLEVEL1,
    RESEARCH_ZERGMELEEWEAPONSLEVEL2,
    RESEARCH_ZERGMELEEWEAPONSLEVEL3,
    SCV,
    SPAWNINGPOOL,
    ULTRALISK,
    ULTRALISKCAVERN,
    UPGRADETOHIVE_HIVE,
    UPGRADETOLAIR_LAIR,
    ZERGGROUNDARMORSLEVEL3,
    ZERGLING,
    ZERGLINGATTACKSPEED,
    ZERGMELEEWEAPONSLEVEL3,
)

from sc2.player import Bot, Computer
from army import army_control
from worker import worker_control
from creep_spread import creep_control
from upgrades import upgrades_control
from buildings import builder


# noinspection PyMissingConstructor
class EarlyAggro(sc2.BotAI, army_control, worker_control, creep_control, upgrades_control, builder):
    """It makes one attack early then tried to make a very greedy transition"""

    def __init__(self):
        worker_control.__init__(self)
        builder.__init__(self)
        self.worker_to_first_base = False
        self.close_enemies_to_base = False
        self.actions = []
        self.used_tumors = []
        self.locations = []
        self.location_index = 0
        self.abilities_list = {
            RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            RESEARCH_ZERGGROUNDARMORLEVEL1,
            RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            RESEARCH_ZERGGROUNDARMORLEVEL2,
            RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            RESEARCH_ZERGGROUNDARMORLEVEL3,
        }

    async def on_step(self, iteration):
        self.actions = []
        self.close_enemies_to_base = False
        if iteration == 0:
            self.actions.append(self.units(OVERLORD).first.move(self._game_info.map_center))
            self.locations = list(self.expansion_locations.keys())
            await self.split_workers()
        if self.known_enemy_units.not_structure:  # I only go to the loop if possibly needed
            for hatch in self.townhalls:
                close_enemy = self.known_enemy_units.not_structure.closer_than(40, hatch.position)
                enemies = close_enemy.exclude_type([DRONE, SCV, PROBE])
                if enemies:
                    self.close_enemies_to_base = True
                    break
        await self.all_buildings()
        await self.all_upgrades()
        await self.army_micro()
        await self.build_units()
        await self.build_queens()
        await self.cancel_attacked_hatcheries()
        await self.defend_worker_rush()
        await self.detection()
        await self.distribute_workers()
        await self.finding_bases()
        await self.morphing_townhalls()
        await self.queens_abilities()
        await self.spread_creep()
        await self.do_actions(self.actions)

    async def build_overlords(self):
        """We do not get supply blocked, but builds one more overlord than needed at some points"""
        if not self.supply_cap >= 200 and self.supply_left < 8:
            if self.can_afford(OVERLORD):
                base_amount = len(self.townhalls)  # so it just calculate once per loop
                if (
                    len(self.units(DRONE).ready) == 14
                    or (len(self.units(OVERLORD)) == 2 and base_amount == 1)
                    or (base_amount == 2 and not self.units(SPAWNINGPOOL))
                ):
                    return False
                if (base_amount in (1, 2) and self.already_pending(OVERLORD)) or (self.already_pending(OVERLORD) >= 3):
                    return False
                self.actions.append(self.units(LARVA).random.train(OVERLORD))
                return True
            return False

    async def build_queens(self):
        """It possibly can get better but it seems good enough for now"""
        queens = self.units(QUEEN)
        hatchery = self.townhalls.exclude_type(LAIR).ready
        if hatchery.noqueue and self.units(SPAWNINGPOOL).ready:
            hatcheries_random = hatchery.noqueue.random
            if (
                len(queens) < len(hatchery) + 1
                and not self.already_pending(QUEEN)
                and self.can_feed(QUEEN)
                and self.can_afford(QUEEN)
            ):
                self.actions.append(hatcheries_random.train(QUEEN))

    async def build_ultralisk(self):
        """Good for now but it might need to be changed vs particular
         enemy units compositions"""
        if self.units(ULTRALISKCAVERN).ready:
            if self.can_afford(ULTRALISK) and self.can_feed(ULTRALISK):
                self.actions.append(self.units(LARVA).random.train(ULTRALISK))
                return True
            return False

    async def build_zerglings(self):
        """good enough for now"""
        larva = self.units(LARVA)
        if self.units(SPAWNINGPOOL).ready:
            if self.can_afford(ZERGLING) and self.can_feed(ZERGLING):
                if self.units(ULTRALISKCAVERN).ready and self.time < 1380:
                    if len(self.units(ULTRALISK)) * 8 > len(self.units(ZERGLING)):
                        self.actions.append(larva.random.train(ZERGLING))
                        return True
                else:
                    self.actions.append(larva.random.train(ZERGLING))
                    return True
            return False

    async def build_units(self):
        """ Build one unit, the most prioritized at the moment """
        if self.units(LARVA):
            available_units_in_order = (
                self.build_ultralisk,
                self.build_overlords,
                self.build_workers,
                self.build_zerglings,
            )
            for build_unit_function in available_units_in_order:
                want_to_built_unit = await build_unit_function()
                if want_to_built_unit:
                    break

    async def cancel_attacked_hatcheries(self):
        """find the hatcheries that are building, and have low health and cancel then,
        can be better, its easy to burst 150 hp, but if I put more it might cancel itself,
        will look into that later"""
        for building in self.units(HATCHERY).filter(lambda x: 0.2 < x.build_progress < 1 and x.health < 400):
            self.actions.append(building(CANCEL))

    async def detection(self):
        """Morph overseers"""
        lords = self.units(OVERLORD)
        if (
            (self.units(LAIR) or self.units(HIVE))
            and self.can_afford(OVERSEER)
            and lords
            and not self.units(OVERSEER)
            and not any([await self.is_morphing(h) for h in self.units(OVERLORDCOCOON)])
        ):
            self.actions.append(lords.random(MORPH_OVERSEER))

    async def finding_bases(self):
        """Find hidden bases, slowly"""
        if self.time >= 720 and self.time % 20 == 0:
            location = self.locations[self.location_index]
            if self.workers:
                self.actions.append(self.workers.closest_to(location).move(location))
                self.location_index = (self.location_index + 1) % len(self.locations)

    async def is_morphing(self, homecity):
        """Check if a base or overlord is morphing, good enough for now"""
        abilities = await self.get_available_abilities(homecity)
        morphing_upgrades = (CANCEL_MORPHLAIR, CANCEL_MORPHHIVE, CANCEL_MORPHOVERSEER)
        for morph in morphing_upgrades:
            if morph in abilities:
                return True
        return False

    async def morphing_townhalls(self):
        """Works well, maybe the timing can be improved"""
        if not (
            all(
                i == 1
                for i in (
                    self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL3),
                    self.already_pending_upgrade(ZERGMELEEWEAPONSLEVEL3),
                    self.already_pending_upgrade(ZERGLINGATTACKSPEED),
                )
            )
            and self.units(ULTRALISKCAVERN).ready
        ):

            lair = self.units(LAIR)
            hive = self.units(HIVE)
            base = self.units(HATCHERY)
            # Hive
            if (
                self.units(INFESTATIONPIT).ready
                and not hive
                and self.can_afford(HIVE)
                and not any([await self.is_morphing(h) for h in lair])
                and lair.ready.idle
            ):
                self.actions.append(lair.ready.idle.first(UPGRADETOHIVE_HIVE))
            # Lair
            if (
                len(self.townhalls) >= 3
                and self.can_afford(UPGRADETOLAIR_LAIR)
                and not (lair or hive)
                and not any([await self.is_morphing(h) for h in base])
                and self.units(HATCHERY).ready.idle
            ):
                self.actions.append(base.ready.idle.furthest_to(self._game_info.map_center)(UPGRADETOLAIR_LAIR))

    async def queens_abilities(self):
        """Injection and creep spread"""
        queens = self.units(QUEEN)
        hatchery = self.townhalls
        if hatchery:
            # lowhp_ultralisks = self.units(ULTRALISK).filter(lambda lhpu: lhpu.health_percentage < 0.27)
            for queen in queens.idle:
                # if not lowhp_ultralisks.closer_than(8, queen.position):
                selected = hatchery.closest_to(queen.position)
                if queen.energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                    self.actions.append(queen(EFFECT_INJECTLARVA, selected))
                    continue
                elif queen.energy >= 26:
                    await self.place_tumor(queen)

                # elif queen.energy >= 50:
                #     self.actions.append(queen(TRANSFUSION_TRANSFUSION, lowhp_ultralisks.closest_to(queen.position)))

            for hatch in hatchery.ready.noqueue:
                if not queens.closer_than(4, hatch):
                    for queen in queens:
                        if not self.townhalls.closer_than(4, queen):
                            self.actions.append(queen.move(hatch.position))
                            break
