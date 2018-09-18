"""SC2 zerg bot by Matuiss, Thommath and Tweakimp"""
import math

import sc2
from sc2 import Difficulty, Race, maps, run_game  # do we need these here?
from sc2.constants import (
    ADEPTPHASESHIFT,
    AUTOTURRET,
    BUILD_CREEPTUMOR_QUEEN,
    BUILD_CREEPTUMOR_TUMOR,
    BUNKER,
    CANCEL,
    CANCEL_MORPHHIVE,
    CANCEL_MORPHLAIR,
    CANCEL_MORPHOVERSEER,
    CHITINOUSPLATING,
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    CREEPTUMORQUEEN,
    DISRUPTORPHASED,
    DRONE,
    EFFECT_INJECTLARVA,
    EGG,
    EVOLUTIONCHAMBER,
    EXTRACTOR,
    HATCHERY,
    HIVE,
    INFESTATIONPIT,
    INFESTEDTERRAN,
    INFESTEDTERRANSEGG,
    LAIR,
    LARVA,
    MORPH_OVERSEER,
    OVERLORD,
    OVERLORDCOCOON,
    OVERLORDSPEED,
    OVERSEER,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    PROBE,
    QUEEN,
    QUEENSPAWNLARVATIMER,
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
    ZERGMELEEWEAPONSLEVEL3,
)
from sc2.data import ActionResult  # for tumors
from sc2.player import Bot, Computer  # do we need these?
from sc2.position import Point2  # for tumors


# noinspection PyMissingConstructor
class EarlyAggro(sc2.BotAI):
    """It makes one attack early then tried to make a very greedy transition"""

    def __init__(self):

        self.worker_to_first_base = False
        self.workers_to_first_extractor = False
        self.enemy_flying_dmg_units = False
        self.worker_to_second_base = False
        self.actions = []
        self.close_enemies = []
        self.used_tumors = []
        self.abilities_list = {
            RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            RESEARCH_ZERGGROUNDARMORLEVEL1,
            RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            RESEARCH_ZERGGROUNDARMORLEVEL2,
            RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            RESEARCH_ZERGGROUNDARMORLEVEL3,
        }
        self.research_list = {RESEARCH_ZERGLINGMETABOLICBOOST, RESEARCH_ZERGLINGADRENALGLANDS}

    async def on_step(self, iteration):
        self.close_enemies = []
        self.actions = []
        if self.known_enemy_units.not_structure:  # I only go to the loop if possibly needed
            for hatch in self.townhalls:
                close_enemy = self.known_enemy_units.not_structure.closer_than(35, hatch.position)
                enemies = close_enemy.exclude_type([DRONE, SCV, PROBE])
                if enemies:
                    self.close_enemies.append(1)
        await self.all_buildings()
        await self.all_upgrades()
        await self.build_extractor()
        await self.build_hatchery()
        await self.build_units()
        await self.build_queens()
        await self.cancel_attacked_hatcheries()
        await self.defend_worker_rush()
        await self.detection()
        await self.distribute_workers()
        await self.micro()
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
            if (
                self.units(HATCHERY)
                and not self.already_pending_upgrade(OVERLORDSPEED)
                and self.can_afford(RESEARCH_PNEUMATIZEDCARAPACE)
            ):
                chosen_base = self.units(HATCHERY).random
                self.actions.append(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))
        # Pool upgrades
        if self.research_list and pool.idle:
            available_research = await self.get_available_abilities(pool.first)
            for research in self.research_list:
                if research in available_research and self.can_afford(research):
                    self.actions.append(pool.first(research))
                    self.research_list.remove(research)
                    break

    async def all_buildings(self):
        """Builds every building, logic should be improved"""
        evochamber = self.units(EVOLUTIONCHAMBER)
        pool = self.units(SPAWNINGPOOL)
        spores = self.units(SPORECRAWLER)
        hatchery = self.units(HATCHERY)
        if pool.ready:
            # Evochamber
            if (
                self.abilities_list
                and self.can_afford(EVOLUTIONCHAMBER)
                and self.townhalls.ready.amount >= 3
                and evochamber.amount < 2
                and not self.already_pending(EVOLUTIONCHAMBER)
            ):
                await self.build(EVOLUTIONCHAMBER, near=pool.first.position.towards(self._game_info.map_center, 3))
            # Spore crawlers
            if not self.enemy_flying_dmg_units:
                if self.known_enemy_units.flying:
                    air_units = [au for au in self.known_enemy_units.flying if au.can_attack_ground]
                    if air_units:
                        self.enemy_flying_dmg_units = True
            else:
                if self.townhalls:
                    selected_base = self.townhalls.random
                    if spores.amount < self.townhalls.ready.amount:
                        if (
                            not spores.closer_than(15, selected_base.position)
                            and self.can_afford(SPORECRAWLER)
                            and not self.already_pending(SPORECRAWLER)
                        ):
                            await self.build(SPORECRAWLER, near=selected_base.position)
        # Infestor pit
        if (
            not self.units(INFESTATIONPIT)
            and self.can_afford(INFESTATIONPIT)
            and not self.already_pending(INFESTATIONPIT)
            and self.units(LAIR).ready
            and self.townhalls
            and evochamber
        ):
            await self.build(INFESTATIONPIT, near=evochamber.first.position)
        # Spawning pool
        if (
            not pool
            and self.can_afford(SPAWNINGPOOL)
            and not self.already_pending(SPAWNINGPOOL)
            and hatchery.amount >= 2
        ):
            await self.build(SPAWNINGPOOL, near=hatchery.first.position.towards(self._game_info.map_center, 5))
        # Ultra cavern
        if (
            self.units(HIVE)
            and not self.units(ULTRALISKCAVERN)
            and self.can_afford(ULTRALISKCAVERN)
            and not self.already_pending(ULTRALISKCAVERN)
            and evochamber
        ):
            await self.build(ULTRALISKCAVERN, near=evochamber.random.position)

    async def build_extractor(self):
        """Couldnt find another way to build the geysers its way to inefficient"""
        gas = self.units(EXTRACTOR)
        pit = self.units(INFESTATIONPIT)
        # check for ressources here to not always call "closer_than"
        if self.townhalls.ready and self.can_afford(EXTRACTOR) and not self.already_pending(EXTRACTOR):
            vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.ready.random)
            for geyser in vgs:
                if self.can_afford(EXTRACTOR):
                    drone = self.select_build_worker(geyser.position)
                    if not drone:
                        break
                    if not gas and self.units(HATCHERY).amount == 2:
                        self.actions.append(drone.build(EXTRACTOR, geyser))
                        break
                    elif gas.amount < 2 and self.units(EVOLUTIONCHAMBER).ready.amount == 2:
                        self.actions.append(drone.build(EXTRACTOR, geyser))
                        break
                    elif self.time > 900 and gas.amount < 9:
                        self.actions.append(drone.build(EXTRACTOR, geyser))
                        break
                    elif pit:
                        if gas.amount < 7:
                            self.actions.append(drone.build(EXTRACTOR, geyser))
                            break
        if not self.workers_to_first_extractor:
            if gas.ready:
                self.workers_to_first_extractor = True
                extractor = gas.first
                for worker in self.workers.gathering.random_group_of(3):
                    self.actions.append(worker.gather(extractor))

    async def build_hatchery(self):
        """Good for now, might be way too greedy tho(might need static defense)
        Logic can be improved, the way to check for close enemies is way to inefficient"""
        if not self.worker_to_first_base and self.townhalls.amount < 2 and self.minerals > 175:
            self.worker_to_first_base = True
            self.actions.append(self.workers.gathering.first.move(await self.get_next_expansion()))
        if (
            self.worker_to_first_base
            and not self.worker_to_second_base
            and self.townhalls.amount == 2
            and self.units(SPAWNINGPOOL)
            and self.minerals > 125
        ):
            self.worker_to_second_base = True
            self.actions.append(self.workers.gathering.random.move(await self.get_next_expansion()))
        if self.townhalls.exists and self.can_afford(HATCHERY) and not self.close_enemies:
            if self.townhalls.amount < 3:
                await self.expand_now()
            if not self.already_pending(HATCHERY):
                if self.townhalls.amount == 3 and self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL1) > 0:
                    await self.expand_now()
                elif self.townhalls.amount == 4 and self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL2) > 0.3:
                    await self.expand_now()
                elif self.units(ULTRALISK).amount >= 2:
                    await self.expand_now()

    async def build_overlords(self):
        """We do not get supply blocked, but builds one more overlord than needed at some points"""
        if not self.supply_cap >= 200 and self.supply_left < 8:
            if self.can_afford(OVERLORD):
                if self.townhalls.amount in (1, 2) and self.already_pending(OVERLORD):
                    return False
                if self.already_pending(OVERLORD) >= 2:
                    return False
                self.actions.append(self.units(LARVA).random.train(OVERLORD))
                return True
            return False
        return False

    async def build_queens(self):
        """Its really bad at the moment, but this will do for now,
        since I removed it from the build_units function, I might be able to remove the returns"""
        queens = self.units(QUEEN)
        hatchery = self.townhalls.exclude_type(LAIR).ready
        if hatchery.noqueue and self.units(SPAWNINGPOOL).ready:
            hatcheries_random = hatchery.noqueue.random
            if (
                queens.amount < hatchery.amount + 1
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
        return False

    async def build_workers(self):
        """Good for the beginning, but it doesnt adapt to losses of drones very well,
        Logic can be improved, the way to check for close enemies is way to inefficient"""
        workers_total = self.workers.amount
        larva = self.units(LARVA)
        geysirs = self.units(EXTRACTOR)
        if not self.close_enemies and self.can_afford(DRONE) and self.can_feed(DRONE):
            if workers_total == 12 and not self.already_pending(DRONE):
                self.actions.append(larva.random.train(DRONE))
                return True
            if (
                workers_total in (13, 14, 15)
                and self.can_afford(DRONE)
                and self.can_feed(DRONE)
                and self.units(OVERLORD).amount + self.already_pending(OVERLORD) > 1
            ):
                if workers_total == 15 and geysirs.exists and self.units(SPAWNINGPOOL).exists:
                    self.actions.append(larva.random.train(DRONE))
                    return True
                else:
                    self.actions.append(larva.random.train(DRONE))
                    return True
                  
            if self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) == 1:
                optimal_workers = min(sum([x.ideal_harvesters for x in self.townhalls | geysirs]), 92)
                if workers_total + self.already_pending(DRONE) < optimal_workers:
                    self.actions.append(larva.random.train(DRONE))
                    return True

    async def build_zerglings(self):
        """good enough for now"""
        larva = self.units(LARVA)
        if self.units(SPAWNINGPOOL).ready:
            if self.can_afford(ZERGLING) and self.can_feed(ZERGLING) and self.units(ZERGLING).amount < 106:
                if self.units(ULTRALISKCAVERN).ready and self.time < 1380:
                    if self.units(ULTRALISK).amount * 8 > self.units(ZERGLING).amount:
                        self.actions.append(larva.random.train(ZERGLING))
                        return True
                else:
                    self.actions.append(larva.random.train(ZERGLING))
                    return True
            return False
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
        """find the hatcheries that are building, and have low health. And cancel then"""
        for building in self.units(HATCHERY).filter(lambda x: 0.3 < x.build_progress < 1 and x.health < 150):
            self.actions.append(building(CANCEL))

    async def defend_worker_rush(self):
        """Its the way I found to defend simple worker rushes,
         I don't know if it beats complexes worker rushes like tyr's bot,
        also it follows scouting workers all the way"""
        base = self.units(HATCHERY)
        if self.known_enemy_units and base:
            enemy_units_close = self.known_enemy_units.closer_than(5, base.first).of_type([PROBE, DRONE, SCV])
            if enemy_units_close and self.townhalls.amount < 2:
                if len(enemy_units_close) == 1:
                    selected_worker = self.workers.first
                    self.actions.append(
                        selected_worker.attack(self.known_enemy_units.closest_to(selected_worker.position))
                    )
                else:
                    for worker in self.workers:
                        self.actions.append(worker.attack(self.known_enemy_units.closest_to(worker.position)))

    async def detection(self):
        """Morph overseers"""
        lords = self.units(OVERLORD)
        if (
            self.units(ULTRALISKCAVERN).ready
            and self.can_afford(OVERSEER)
            and lords
            and not self.units(OVERSEER)
            and not any([await self.is_morphing(h) for h in self.units(OVERLORDCOCOON)])
        ):
            self.actions.append(lords.random(MORPH_OVERSEER))

    async def is_morphing(self, homecity):
        """Check if a base is morphing, good enough for now"""
        abilities = await self.get_available_abilities(homecity)
        morphing_upgrades = (CANCEL_MORPHLAIR, CANCEL_MORPHHIVE, CANCEL_MORPHOVERSEER)
        for morph in morphing_upgrades:
            if morph in abilities:
                return True
        return False

    async def micro(self):
        """Micro function, its just slight better than a-move, need A LOT of improvements"""
        enemy_build = self.known_enemy_structures
        excluded_units = {ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA, INFESTEDTERRANSEGG, INFESTEDTERRAN, AUTOTURRET}
        filtered_enemies = self.known_enemy_units.not_structure.exclude_type(excluded_units)
        static_defence = self.known_enemy_units.of_type({SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS})
        target = static_defence | filtered_enemies.not_flying
        atk_force = self.units(ZERGLING) | self.units(ULTRALISK)
        for attacking_unit in atk_force:
            if target.closer_than(47, attacking_unit.position):
                self.actions.append(attacking_unit.attack(target.closest_to(attacking_unit.position)))
                continue  # these continues are needed so a unit doesnt get multiple orders per step
            elif enemy_build.closer_than(27, attacking_unit.position):
                self.actions.append(attacking_unit.attack(enemy_build.closest_to(attacking_unit.position)))
                continue
            elif self.time < 235:
                if atk_force.amount <= 25:
                    self.actions.append(
                        attacking_unit.move(self._game_info.map_center.towards(self.enemy_start_locations[0], 11))
                    )
                    continue
                elif attacking_unit.position.distance_to(self.enemy_start_locations[0]) > 0 and atk_force.amount > 25:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
                continue
            elif self.time < 1000:
                if self.units(ULTRALISK).amount < 4 and self.supply_used not in range(198, 201):
                    self.actions.append(attacking_unit.move(self._game_info.map_center))
                    continue
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
                    continue

            else:
                if enemy_build:
                    self.actions.append(attacking_unit.attack(enemy_build.closest_to(attacking_unit.position)))
                    continue
                elif target:
                    self.actions.append(attacking_unit.attack(target.closest_to(attacking_unit.position)))
                    continue
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
                    continue
        for detection in self.units(OVERSEER):
            if atk_force:
                self.actions.append(detection.move(atk_force.closest_to(detection.position)))
                continue

    async def morphing_townhalls(self):
        """Works well, maybe the timing can be improved"""
        lair = self.units(LAIR)
        hive = self.units(HIVE)
        base = self.units(HATCHERY)
        if not (
            all(
                i == 1
                for i in (
                    self.already_pending(ZERGGROUNDARMORSLEVEL3),
                    self.already_pending(ZERGMELEEWEAPONSLEVEL3),
                    self.already_pending(ZERGLINGATTACKSPEED),
                )
            )
            and self.units(ULTRALISKCAVERN).ready
        ):
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
                self.townhalls.amount >= 3
                and self.can_afford(UPGRADETOLAIR_LAIR)
                and not (lair or hive)
                and not any([await self.is_morphing(h) for h in base])
                and self.units(HATCHERY).ready.idle
            ):
                self.actions.append(base.ready.idle.furthest_to(self._game_info.map_center)(UPGRADETOLAIR_LAIR))

    async def place_tumor(self, unit):
        """ Find a nice placement for the tumor and build it if possible.
        Makes creep to the center, needs a better value function for the spreading """
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
        if valid_placements:
            self.actions.append(unit(unit_ability, valid_placements[0]))
            if unit_ability == BUILD_CREEPTUMOR_TUMOR:  # if tumor
                self.used_tumors.append(unit.tag)

    async def queens_abilities(self):
        """Injection and creep spread"""
        queens = self.units(QUEEN)
        hatchery = self.townhalls
        if hatchery:
            for queen in queens.idle:
                selected = hatchery.closest_to(queen.position)
                if queen.energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                    self.actions.append(queen(EFFECT_INJECTLARVA, selected))

                elif queen.energy > 26:
                    await self.place_tumor(queen)
            for hatch in hatchery.ready.noqueue:
                if not queens.closer_than(8, hatch):
                    for queen in queens:
                        if not self.townhalls.closer_than(8, queen):
                            self.actions.append(queen.move(hatch.position))
                            break

    async def spread_creep(self):
        """ Iterate over all tumors to spread itself """
        tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)
        for tumor in tumors:
            if tumor.tag not in self.used_tumors:
                await self.place_tumor(tumor)
