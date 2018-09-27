"""SC2 zerg bot by Matuiss, Thommath and Tweakimp"""
import math
import sc2
from sc2 import Difficulty, Race, maps, run_game
from sc2.constants import (
    BUILD_CREEPTUMOR_QUEEN,
    BUILD_CREEPTUMOR_TUMOR,
    BURROW,
    CANCEL,
    CANCEL_MORPHHIVE,
    CANCEL_MORPHLAIR,
    CANCEL_MORPHOVERSEER,
    CHITINOUSPLATING,
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    CREEPTUMORQUEEN,
    DRONE,
    EFFECT_INJECTLARVA,
    EVOLUTIONCHAMBER,
    EXTRACTOR,
    HATCHERY,
    HIVE,
    INFESTATIONPIT,
    LAIR,
    LARVA,
    MORPH_OVERSEER,
    OBSERVER,
    OVERLORD,
    OVERLORDCOCOON,
    OVERLORDSPEED,
    OVERSEER,
    PROBE,
    QUEEN,
    QUEENSPAWNLARVATIMER,
    RESEARCH_BURROW,
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
    SCV,
    SPAWNINGPOOL,
    SPINECRAWLER,
    SPORECRAWLER,
    TRANSFUSION_TRANSFUSION,
    ULTRALISK,
    ULTRALISKCAVERN,
    UPGRADETOHIVE_HIVE,
    UPGRADETOLAIR_LAIR,
    ZERGBUILD_CREEPTUMOR,
    ZERGGROUNDARMORSLEVEL1,
    ZERGGROUNDARMORSLEVEL2,
    ZERGGROUNDARMORSLEVEL3,
    ZERGLING,
    ZERGLINGATTACKSPEED,
    ZERGLINGMOVEMENTSPEED,
    ZERGMELEEWEAPONSLEVEL1,
    ZERGMELEEWEAPONSLEVEL3,
)
from sc2.data import ActionResult  # for tumors
from sc2.player import Bot, Computer
from sc2.position import Point2  # for tumors

from army import army_control
from worker import worker_control


# noinspection PyMissingConstructor
class EarlyAggro(sc2.BotAI, army_control, worker_control):
    """It makes one attack early then tried to make a very greedy transition"""

    def __init__(self):
        worker_control.__init__(self)
        self.worker_to_first_base = False
        self.workers_to_first_extractor = False
        self.enemy_flying_dmg_units = False
        self.worker_to_second_base = False
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
        await self.build_extractor()
        await self.build_hatchery()
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

    async def all_upgrades(self):
        """All used upgrades, maybe can be optimized"""
        # Evochamber
        evochamber = self.units(EVOLUTIONCHAMBER).ready
        cavern = self.units(ULTRALISKCAVERN).ready
        pool = self.units(SPAWNINGPOOL).ready
        if self.abilities_list and evochamber.idle:
            for evo in evochamber.idle:
                abilities = await self.get_available_abilities(evo)
                for ability in self.abilities_list:
                    if ability in abilities:
                        if self.can_afford(ability):
                            self.actions.append(evo(ability))
                            self.abilities_list.remove(ability)
                            break
        # Ultralisk armor and Hatchery upgrades
        if cavern:
            if self.already_pending_upgrade(CHITINOUSPLATING) == 0 and self.can_afford(CHITINOUSPLATING):
                self.actions.append(cavern.idle.first(RESEARCH_CHITINOUSPLATING))
            if self.units(HATCHERY):
                if not self.already_pending_upgrade(OVERLORDSPEED) and self.can_afford(RESEARCH_PNEUMATIZEDCARAPACE):
                    chosen_base = self.units(HATCHERY).random
                    self.actions.append(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))
                # if not self.already_pending_upgrade(BURROW) and self.can_afford(RESEARCH_BURROW):
                #     chosen_base = self.units(HATCHERY).random
                #     self.actions.append(chosen_base(RESEARCH_BURROW))

        if pool.idle:
            if not self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) or not self.already_pending_upgrade(
                ZERGLINGATTACKSPEED
            ):
                if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST):
                    self.actions.append(pool.first(RESEARCH_ZERGLINGMETABOLICBOOST))
                if self.can_afford(RESEARCH_ZERGLINGADRENALGLANDS):
                    self.actions.append(pool.first(RESEARCH_ZERGLINGADRENALGLANDS))

    async def all_buildings(self):
        """Builds every building, logic should be improved"""
        evochamber = self.units(EVOLUTIONCHAMBER)
        pool = self.units(SPAWNINGPOOL)
        spores = self.units(SPORECRAWLER)
        base = self.townhalls  # so it just access the library once every loop instead of several
        if pool.ready:
            finished_base_amount = len(base.ready)  # same as above, calculate just once
            # Evochamber
            if (
                self.abilities_list
                and self.can_afford(EVOLUTIONCHAMBER)
                and finished_base_amount == 3
                and len(evochamber) < 2
                and not self.already_pending(EVOLUTIONCHAMBER)
            ):
                if not evochamber:
                    await self.build(EVOLUTIONCHAMBER, pool.first.position.towards(self._game_info.map_center, 3))
                elif self.already_pending_upgrade(ZERGMELEEWEAPONSLEVEL1) > .25:
                    await self.build(EVOLUTIONCHAMBER, pool.first.position.towards(self._game_info.map_center, 3))
            # Spore crawlers
            if not self.enemy_flying_dmg_units:
                if self.known_enemy_units.flying:
                    air_units = [au for au in self.known_enemy_units.flying if au.can_attack_ground]
                    if air_units:
                        self.enemy_flying_dmg_units = True
            else:
                if base:
                    selected_base = base.random
                    if len(spores) + self.already_pending(SPORECRAWLER) < finished_base_amount:
                        if not spores.closer_than(15, selected_base.position) and self.can_afford(SPORECRAWLER):
                            await self.build(SPORECRAWLER, near=selected_base.position)
            if len(base.ready) >= 2 and self.time < 360:
                if len(self.units(SPINECRAWLER)) < 3 and not self.already_pending(SPINECRAWLER):
                    await self.build(
                        SPINECRAWLER,
                        self.townhalls.closest_to(self._game_info.map_center).position.towards(
                            self._game_info.map_center, 11
                        ),
                    )
        if evochamber:
            # Infestor pit
            if (
                not self.units(INFESTATIONPIT)
                and self.can_afford(INFESTATIONPIT)
                and not self.already_pending(INFESTATIONPIT)
                and self.units(LAIR).ready
                and (self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL2) > 0)
                and base
            ):
                await self.build(INFESTATIONPIT, near=evochamber.first.position)
            # Ultra cavern
            if (
                self.units(HIVE)
                and not self.units(ULTRALISKCAVERN)
                and self.can_afford(ULTRALISKCAVERN)
                and not self.already_pending(ULTRALISKCAVERN)
            ):
                await self.build(ULTRALISKCAVERN, near=evochamber.random.position)

        # Spawning pool
        if not pool and self.can_afford(SPAWNINGPOOL) and not self.already_pending(SPAWNINGPOOL) and len(base) >= 2:
            await self.build(SPAWNINGPOOL, base.first.position.towards(self._game_info.map_center, 5))

    async def build_extractor(self):
        """Couldnt find another way to build the geysers its way to inefficient
        Check for resources here to not always call "closer_than" """
        if self.townhalls.ready and self.can_afford(EXTRACTOR):
            gas = self.units(EXTRACTOR)
            gas_amount = len(gas)  # so it calculate just once per step
            vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.ready.random)
            for geyser in vgs:
                drone = self.select_build_worker(geyser.position)
                if not drone:
                    break
                if not self.already_pending(EXTRACTOR):
                    if not gas and len(self.townhalls) >= 3:
                        self.actions.append(drone.build(EXTRACTOR, geyser))
                        break
                    if gas_amount < 2 and len(self.workers) >= 40:
                        self.actions.append(drone.build(EXTRACTOR, geyser))
                        break
                if self.time > 900 and gas_amount < 9:
                    self.actions.append(drone.build(EXTRACTOR, geyser))
                    break

                pit = self.units(INFESTATIONPIT)
                if pit and gas_amount + self.already_pending(EXTRACTOR) < 7:
                    self.actions.append(drone.build(EXTRACTOR, geyser))
                    break

    async def build_hatchery(self):
        """Good for now, might be way too greedy tho(might need static defense)
        Logic can be improved, the way to check for close enemies is way to inefficient"""
        base_amount = len(self.townhalls)  # so it just calculate once per loop
        if not self.worker_to_first_base and base_amount < 2 and self.minerals > 235:
            self.worker_to_first_base = True
            self.actions.append(self.workers.gathering.first.move(await self.get_next_expansion()))
        if (
            self.townhalls
            and self.can_afford(HATCHERY)
            and not self.close_enemies_to_base
            and not self.already_pending(HATCHERY)
        ):
            if base_amount <= 4:
                await self.expand_now()
            elif self.units(ULTRALISKCAVERN):
                await self.expand_now()

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

    async def build_workers(self):
        """Good for the beginning, but it doesnt adapt to losses of drones very well"""
        workers_total = len(self.workers)
        larva = self.units(LARVA)
        geysirs = self.units(EXTRACTOR)
        if not self.close_enemies_to_base and self.can_afford(DRONE) and self.can_feed(DRONE):
            if workers_total == 12 and not self.already_pending(DRONE):
                self.actions.append(larva.random.train(DRONE))
                return True
            if workers_total in (13, 14, 15) and len(self.units(OVERLORD)) + self.already_pending(OVERLORD) > 1:
                if workers_total == 15 and geysirs and self.units(SPAWNINGPOOL):
                    self.actions.append(larva.random.train(DRONE))
                    return True
                self.actions.append(larva.random.train(DRONE))
                return True

            optimal_workers = min(sum([x.ideal_harvesters for x in self.townhalls | geysirs]), 92 - len(geysirs))
            if workers_total + self.already_pending(DRONE) < optimal_workers and self.units(ZERGLING).exists:
                self.actions.append(larva.random.train(DRONE))
                return True

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

    async def place_tumor(self, unit):
        """ Find a nice placement for the tumor and build it if possible, avoid expansion locations
        Makes creep to the enemy base, needs a better value function for the spreading"""
        # Make sure unit can make tumor and what ability it is
        abilities = await self.get_available_abilities(unit)
        if BUILD_CREEPTUMOR_QUEEN in abilities:
            unit_ability = BUILD_CREEPTUMOR_QUEEN
        elif BUILD_CREEPTUMOR_TUMOR in abilities:
            unit_ability = BUILD_CREEPTUMOR_TUMOR
        else:
            return

        # defining vars
        ability = self._game_data.abilities[ZERGBUILD_CREEPTUMOR.value]
        location_attempts = 30
        spread_distance = 8
        location = unit.position
        # Define random positions around unit
        positions = [
            Point2(
                (
                    location.x + spread_distance * math.cos(math.pi * alpha * 2 / location_attempts),
                    location.y + spread_distance * math.sin(math.pi * alpha * 2 / location_attempts),
                )
            )
            for alpha in range(location_attempts)
        ]
        # check if any of the positions are valid
        valid_placements = await self._client.query_building_placement(ability, positions)
        # filter valid results
        valid_placements = [p for index, p in enumerate(positions) if valid_placements[index] == ActionResult.Success]
        if valid_placements:
            tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)
            if tumors:
                valid_placements = sorted(
                    valid_placements,
                    key=lambda pos: pos.distance_to_closest(tumors) - pos.distance_to(self.enemy_start_locations[0]),
                    reverse=True,
                )
            else:
                valid_placements = sorted(
                    valid_placements, key=lambda pos: pos.distance_to(self.enemy_start_locations[0])
                )
            # this is very expensive to the cpu, need optimization, keeps creep outside expansion locations
            for c_location in valid_placements:
                # 8.5 it doesnt get in the way of the injection
                if all(c_location.distance_to(el) > 8.5 for el in self.expansion_locations):
                    if not tumors:
                        self.actions.append(unit(unit_ability, c_location))
                        break
                    if unit_ability == BUILD_CREEPTUMOR_QUEEN:
                        self.actions.append(unit(unit_ability, c_location))
                        break
                    if c_location.distance_to_closest(tumors) >= 4:
                        self.actions.append(unit(unit_ability, c_location))
                        break

            if unit_ability == BUILD_CREEPTUMOR_TUMOR:  # if tumor
                self.used_tumors.append(unit.tag)

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

    async def spread_creep(self):
        """ Iterate over all tumors to spread itself remove used creeps"""
        tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)
        for tumor in tumors:
            if tumor.tag not in self.used_tumors:
                await self.place_tumor(tumor)
