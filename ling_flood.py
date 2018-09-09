"""SC2 zerg bot by Matuiss and Thommath"""
import math
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.constants import HATCHERY, ZERGLING, QUEEN, LARVA, EFFECT_INJECTLARVA, \
    SPAWNINGPOOL, RESEARCH_ZERGLINGMETABOLICBOOST, OVERLORD, EXTRACTOR, DRONE, \
    QUEENSPAWNLARVATIMER, ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, ZERGLINGMOVEMENTSPEED, \
    EVOLUTIONCHAMBER, RESEARCH_ZERGMELEEWEAPONSLEVEL1, RESEARCH_ZERGGROUNDARMORLEVEL1, \
    ZERGGROUNDARMORSLEVEL1, UPGRADETOLAIR_LAIR, RESEARCH_ZERGGROUNDARMORLEVEL2, \
    RESEARCH_ZERGMELEEWEAPONSLEVEL2, SCV, PROBE, INFESTATIONPIT, HIVE, UPGRADETOHIVE_HIVE, \
    RESEARCH_ZERGMELEEWEAPONSLEVEL3, RESEARCH_ZERGGROUNDARMORLEVEL3, LAIR, \
    RESEARCH_ZERGLINGADRENALGLANDS, CANCEL_MORPHLAIR, CANCEL_MORPHHIVE, ULTRALISKCAVERN, \
    RESEARCH_CHITINOUSPLATING, INFESTEDTERRANSEGG, INFESTEDTERRAN, SPINECRAWLER, PHOTONCANNON, \
    BUNKER, PLANETARYFORTRESS, AUTOTURRET, BUILD_CREEPTUMOR_QUEEN, BUILD_CREEPTUMOR_TUMOR, \
    CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED, OVERSEER, CANCEL_MORPHOVERSEER, \
    ZERGBUILD_CREEPTUMOR, ZERGGROUNDARMORSLEVEL3, ZERGMELEEWEAPONSLEVEL3, ZERGLINGATTACKSPEED, \
    OVERLORDCOCOON, SPORECRAWLER, ULTRALISK, MORPH_OVERSEER, RESEARCH_PNEUMATIZEDCARAPACE, \
    CANCEL
from sc2.position import Point2  # for tumors
from sc2.data import ActionResult  # for tumors
from sc2.player import Bot, Computer


class EarlyAggro(sc2.BotAI):
    """It makes one attack early then tried to make a very greedy transition"""

    def __init__(self):
        self.flag1 = False
        self.flag2 = False
        self.flag3 = False
        self.actions = []
        self.close_enemies = []
        self.used_tumors = []

    async def on_step(self, iteration):
        self.close_enemies = []
        self.actions = []
        await self.all_buildings()
        await self.all_upgrades()
        await self.build_extrator()
        await self.build_hatchery()
        await self.build_units()
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
        evochamber = self.units(EVOLUTIONCHAMBER)
        cavern = self.units(ULTRALISKCAVERN)
        pool = self.units(SPAWNINGPOOL).ready
        if evochamber.ready.idle.exists:
            for evo in evochamber.ready.idle:
                abilities = await self.get_available_abilities(evo)
                abilities_list = [RESEARCH_ZERGMELEEWEAPONSLEVEL1,
                                  RESEARCH_ZERGGROUNDARMORLEVEL1,
                                  RESEARCH_ZERGMELEEWEAPONSLEVEL2,
                                  RESEARCH_ZERGGROUNDARMORLEVEL2,
                                  RESEARCH_ZERGMELEEWEAPONSLEVEL3,
                                  RESEARCH_ZERGGROUNDARMORLEVEL3]
                for ability in abilities_list:
                    if ability in abilities:
                        if self.can_afford(ability):
                            self.actions.append(evo(ability))
                            break
        # Ultralisk armor
        if cavern.ready.exists:
            available_research = await self.get_available_abilities(cavern.ready.first)
            if RESEARCH_CHITINOUSPLATING in available_research \
                    and self.can_afford(RESEARCH_CHITINOUSPLATING):
                self.actions.append(cavern.first(RESEARCH_CHITINOUSPLATING))
        # Pool upgrades
        if pool.idle.exists:
            available_research = await self.get_available_abilities(pool.first)
            research_list = [RESEARCH_ZERGLINGMETABOLICBOOST, RESEARCH_ZERGLINGADRENALGLANDS]
            for research in research_list:
                if research in available_research and self.can_afford(research):
                    self.actions.append(pool.first(research))
        # Hatchery upgrades
        if self.units(ULTRALISKCAVERN).ready.exists and self.units(HATCHERY).exists:
            chosen_base = self.units(HATCHERY).random
            if RESEARCH_PNEUMATIZEDCARAPACE in await self.get_available_abilities(chosen_base):
                if self.can_afford(RESEARCH_PNEUMATIZEDCARAPACE):
                    self.actions.append(chosen_base(RESEARCH_PNEUMATIZEDCARAPACE))

    async def all_buildings(self):
        """Builds every building, logic should be improved"""
        evochamber = self.units(EVOLUTIONCHAMBER)
        pool = self.units(SPAWNINGPOOL)
        spores = self.units(SPORECRAWLER)
        air_units = [au for au in self.known_enemy_units.flying if au.can_attack_ground]
        # Evochamber
        if self.can_afford(EVOLUTIONCHAMBER) and self.townhalls.amount >= 3 \
                and evochamber.amount < 2 and pool.exists \
                and not self.already_pending(EVOLUTIONCHAMBER):
            await self.build(EVOLUTIONCHAMBER,
                             near=pool.first.position.towards(self._game_info.map_center, 3))
        # Infestor pit
        if self.can_afford(INFESTATIONPIT) \
                and self.townhalls.exists and not self.already_pending(INFESTATIONPIT):
            if not self.units(INFESTATIONPIT).exists and self.units(LAIR).ready.exists \
                    and self.units(EVOLUTIONCHAMBER).exists:
                await self.build(INFESTATIONPIT, near=self.units(EVOLUTIONCHAMBER).first.position)
        # Spawning pool
        hatchery = self.units(HATCHERY)
        if self.can_afford(SPAWNINGPOOL) and not self.units(SPAWNINGPOOL).exists \
                and not self.already_pending(SPAWNINGPOOL) and hatchery.amount == 2:
            await self.build(SPAWNINGPOOL,
                             near=hatchery.first.position.towards(self._game_info.map_center, 5))
        # Ultra cavern
        if self.units(HIVE).exists and self.can_afford(ULTRALISKCAVERN) \
                and not self.already_pending(ULTRALISKCAVERN) \
                and not self.units(ULTRALISKCAVERN).exists \
                and evochamber.exists:
            await self.build(ULTRALISKCAVERN, near=evochamber.random.position)
        # Spore crawlers
        if self.townhalls.ready.amount >= 3 and pool.ready.exists:
            if air_units and not self.flag3:
                self.flag3 = True
            if self.flag3:
                selected_base = self.townhalls.random
                if spores.amount < self.townhalls.ready.amount:
                    if not spores.closer_than(15, selected_base.position).exists \
                            and self.can_afford(SPORECRAWLER) \
                            and not self.already_pending(SPORECRAWLER):
                        await self.build(SPORECRAWLER, near=selected_base.position)

    async def build_extrator(self):
        """Couldnt find another way to build the gaisers its way to inefficient"""
        gas = self.units(EXTRACTOR)
        pit = self.units(INFESTATIONPIT)
        if self.townhalls.ready.exists:
            vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.ready.random)
            for gaiser in vgs:
                if self.can_afford(EXTRACTOR):
                    drone = self.select_build_worker(gaiser.position)
                    if not drone:
                        break
                    if not gas.exists and self.units(HATCHERY).amount == 2:
                        if not self.already_pending(EXTRACTOR):
                            self.actions.append(drone.build(EXTRACTOR, gaiser))
                            break
                    elif self.units(EVOLUTIONCHAMBER).ready.amount == 2 \
                            and gas.amount < 2 and not self.already_pending(EXTRACTOR):
                        self.actions.append(drone.build(EXTRACTOR, gaiser))
                        break
                    elif self.time > 900 and gas.amount < 9 \
                            and self.already_pending(EXTRACTOR) < 2:
                        self.actions.append(drone.build(EXTRACTOR, gaiser))
                        break
                    elif pit.exists:
                        if not self.already_pending(EXTRACTOR) \
                                and gas.amount < 6:
                            self.actions.append(drone.build(EXTRACTOR, gaiser))
                            break
        if gas.ready.exists and not self.flag2:
            self.flag2 = True
            extractor = gas.first
            for worker in self.workers.random_group_of(3):
                self.actions.append(worker.gather(extractor))

    async def build_hatchery(self):
        """Good for now, might be way too greedy tho(might need static defense)
        Logic can be improved, the way to check for close enemies is way to inefficient"""
        try:
            for hatch in self.townhalls:
                close_enemy = self.known_enemy_units.not_structure.closer_than(35, hatch.position)
                enemies = close_enemy.exclude_type([DRONE, SCV, PROBE])
                if enemies:
                    self.close_enemies.append(1)
            if self.minerals > 175 and self.townhalls.amount < 2 and not self.flag1:
                self.flag1 = True
                self.actions.append(self.workers.first.move(await self.get_next_expansion()))
            if self.can_afford(HATCHERY) and not self.already_pending(HATCHERY) \
                    and not self.close_enemies:
                if self.townhalls.amount < 3:
                    await self.expand_now()
                elif self.townhalls.amount >= 3 \
                        and self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL1) > 0:
                    await self.expand_now()
        except AssertionError:
            print("damn it")

    async def build_overlords(self):
        """We do not get supply blocked, but builds one more overlord than needed at some points"""
        larva = self.units(LARVA)
        if self.supply_left < 8 and not self.supply_cap >= 200:
            if self.can_afford(OVERLORD) and larva.exists:
                if self.townhalls.amount in [1, 2] and self.already_pending(OVERLORD):
                    return False
                if self.already_pending(OVERLORD) >= 2:
                    return False
                self.actions.append(larva.random.train(OVERLORD))
                return True
        return False

    async def build_queens(self):
        """Its really bad at the moment, but this will do for now"""
        queens = self.units(QUEEN)
        hatchery = self.townhalls.exclude_type(LAIR)
        if hatchery.exists:
            hatcheries_random = self.townhalls.random
            if self.units(SPAWNINGPOOL).ready.exists:
                if queens.amount < hatchery.ready.amount + 1 and hatcheries_random.is_ready \
                        and not self.already_pending(QUEEN) \
                        and hatcheries_random.noqueue and self.supply_left > 1:
                    if self.can_afford(QUEEN):
                        if not queens.closer_than(8, hatcheries_random):
                            self.actions.append(hatcheries_random.train(QUEEN))
                            return True
                        if queens.amount == hatchery.ready.amount:
                            self.actions.append(hatcheries_random.train(QUEEN))
                            return True
                        return False
                return False
            return False

    async def build_ultralisk(self):
        """Good for now but it might need to be changed vs particular
         enemy units compositions"""
        larva = self.units(LARVA)
        if self.units(ULTRALISKCAVERN).ready.exists:
            if larva.exists and self.can_afford(ULTRALISK) and self.supply_left > 5:
                self.actions.append(larva.random.train(ULTRALISK))
                return True
        return False

    async def build_workers(self):
        """Good for the beginning, but it doesnt adapt to losses of drones very well,
        Logic can be improved, the way to check for close enemies is way to inefficient"""
        workers_total = self.workers.amount
        larva = self.units(LARVA)
        gaiser = self.units(EXTRACTOR)
        for hacth in self.townhalls:
            enemies = self.known_enemy_units.not_structure.closer_than(
                35, hacth.position).exclude_type([DRONE, SCV, PROBE])
            if enemies:
                self.close_enemies.append(1)
        if not self.close_enemies:
            if workers_total == 12 and larva.exists and not self.already_pending(DRONE):
                self.actions.append(larva.random.train(DRONE))
                return True
            if workers_total in [13, 14, 15] and self.can_afford(DRONE) \
                    and self.supply_left > 0 \
                    and larva.exists \
                    and self.units(OVERLORD).amount + self.already_pending(OVERLORD) > 1:
                if workers_total == 15:
                    if gaiser.exists and self.units(SPAWNINGPOOL).exists:
                        self.actions.append(larva.random.train(DRONE))
                        return True
                else:
                    self.actions.append(larva.random.train(DRONE))
                    return True
            if self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) == 1 \
                    and workers_total < self.townhalls.ready.amount * 19.5 \
                    and larva.exists and workers_total < 92 - gaiser.amount:
                self.actions.append(larva.random.train(DRONE))
                return True
        return False

    async def build_zerglings(self):
        """good enough for now"""
        larva = self.units(LARVA)
        if self.units(SPAWNINGPOOL).ready.exists:
            if (larva.exists and self.can_afford(ZERGLING) and self.supply_left > 0
                    and self.units(ZERGLING).amount < 100) or self.supply_used in range(195, 200):
                if self.units(ULTRALISKCAVERN).ready.exists:
                    if self.units(ULTRALISK).amount * 8 > self.units(ZERGLING).amount:
                        self.actions.append(larva.random.train(ZERGLING))
                        return True
                else:
                    self.actions.append(larva.random.train(ZERGLING))
                    return True
            return False

    async def build_units(self):
        """ Build one unit, the most prioritized at the moment """
        if not self.units(LARVA).exists:
            return
        available_units_in_order = [
            self.build_ultralisk,
            self.build_overlords,
            self.build_queens,
            self.build_workers,
            self.build_zerglings,
        ]
        for build_unit_function in available_units_in_order:
            want_to_built_unit = await build_unit_function()
            if want_to_built_unit:
                break

    async def cancel_attacked_hatcheries(self):
        """find the hatcheries that are building, and have low health. And cancel then"""
        for building in self.units(HATCHERY).filter(
                lambda x: 0.3 < x.build_progress < 1 and x.health < 100):
            self.actions.append(building(CANCEL))

    async def defend_worker_rush(self):
        """Its the way I found to defend simple worker rushes,
         I don't know if it beats complexes worker rushes like tyr's bot,
        also it follows scouting workers all the way"""
        base = self.units(HATCHERY)
        if self.known_enemy_units.exists and base.exists:
            enemy_units_close = self.known_enemy_units.closer_than(
                5, base.first).of_type([PROBE, DRONE, SCV])
            if enemy_units_close.exists and self.townhalls.amount < 2:
                selected_worker = self.workers.first
                if len(enemy_units_close) == 1:
                    self.actions.append(selected_worker.attack(
                        self.known_enemy_units.closest_to(selected_worker.position)))
                else:
                    for worker in self.workers:
                        self.actions.append(worker.attack(
                            self.known_enemy_units.closest_to(worker.position)))

    async def detection(self):
        """Morph overseers"""
        lords = self.units(OVERLORD)
        if self.units(ULTRALISKCAVERN).ready.exists and self.can_afford(OVERSEER) \
                and lords.exists:
            if not any([await self.is_morphing(h) for h in self.units(OVERLORDCOCOON)]):
                if not self.units(OVERSEER).exists:
                    self.actions.append(lords.random(MORPH_OVERSEER))

    async def is_morphing(self, homecity):
        """Check if a base is morphing, good enough for now"""
        abilities = await self.get_available_abilities(homecity)
        morphing_upgrades = [CANCEL_MORPHLAIR, CANCEL_MORPHHIVE, CANCEL_MORPHOVERSEER]
        for morph in morphing_upgrades:
            if morph in abilities:
                return True
        return False

    async def micro(self):
        """Micro function, its just slight better than a-move, need A LOT of improvements"""
        enemy_build = self.known_enemy_structures
        excluded_units = [ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA,
                          INFESTEDTERRANSEGG, INFESTEDTERRAN, AUTOTURRET]
        filtered_enemies = self.known_enemy_units.not_structure.exclude_type(excluded_units)
        static_defence = self.known_enemy_units.of_type([SPINECRAWLER, PHOTONCANNON,
                                                         BUNKER, PLANETARYFORTRESS])
        target = static_defence | filtered_enemies.not_flying
        atk_force = self.units(ZERGLING) | self.units(ULTRALISK)
        for attacking_unit in atk_force:
            if target.closer_than(47, attacking_unit.position).exists:
                self.actions.append(attacking_unit.attack(
                    target.closest_to(attacking_unit.position)))
            elif enemy_build.closer_than(17, attacking_unit.position).exists:
                self.actions.append(attacking_unit.attack(
                    enemy_build.closest_to(attacking_unit.position)))
            elif self.time < 230:
                if atk_force.amount <= 25:
                    self.actions.append(attacking_unit.move(
                        self._game_info.map_center.towards(self.enemy_start_locations[0], 35)))
                elif attacking_unit.position.distance_to(self.enemy_start_locations[0]) > 0 \
                        and atk_force.amount > 25:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
            elif self.time < 800:
                if self.units(ULTRALISK).amount < 4 and self.supply_used not in range(198, 201):
                    self.actions.append(attacking_unit.move(
                        self._game_info.map_center))
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))
            else:
                if enemy_build.exists:
                    self.actions.append(attacking_unit.attack(
                        enemy_build.closest_to(attacking_unit.position)))
                elif target.exists:
                    self.actions.append(attacking_unit.attack(
                        target.closest_to(attacking_unit.position)))
                else:
                    self.actions.append(attacking_unit.attack(self.enemy_start_locations[0]))

        for detection in self.units(OVERSEER):
            if atk_force.exists:
                self.actions.append(detection.move(atk_force.closest_to(detection.position)))

    async def morphing_townhalls(self):
        """Works well, maybe the timing can be improved"""
        lair = self.units(LAIR)
        hive = self.units(HIVE)
        base = self.units(HATCHERY)
        if not (all(i == 1 for i in [self.already_pending(ZERGGROUNDARMORSLEVEL3),
                                     self.already_pending(ZERGMELEEWEAPONSLEVEL3),
                                     self.already_pending(ZERGLINGATTACKSPEED)])
                and self.units(ULTRALISKCAVERN).ready.exists):
            # Hive
            if self.units(INFESTATIONPIT).ready.exists and not hive.exists \
                    and self.can_afford(HIVE) \
                    and not any([await self.is_morphing(h) for h in lair]) \
                    and lair.ready.idle.exists:
                self.actions.append(lair.ready.idle.first(UPGRADETOHIVE_HIVE))
            # Lair
            if self.townhalls.amount >= 3 and self.can_afford(UPGRADETOLAIR_LAIR) \
                    and not (lair.exists or hive.exists) \
                    and not any([await self.is_morphing(h) for h in base]) \
                    and self.units(HATCHERY).ready.idle.exists:
                self.actions.append(base.ready.idle.first(UPGRADETOLAIR_LAIR))

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
        positions = [Point2((location.x + spread_distance *
                             math.cos(math.pi * alpha * 2 / location_attempts),
                             location.y + spread_distance *
                             math.sin(math.pi * alpha * 2 / location_attempts))) for alpha
                     in range(location_attempts)]
        # check if any of the positions are valid
        valid_placements = await self._client.query_building_placement(ability, positions)
        # filter valid results
        valid_placements = [p for index, p in enumerate(positions)
                            if valid_placements[index] == ActionResult.Success]
        if valid_placements:
            tumors = self.units(CREEPTUMORQUEEN) \
                     | self.units(CREEPTUMOR) \
                     | self.units(CREEPTUMORBURROWED)
            if tumors.exists:
                valid_placements = sorted(valid_placements,
                                          key=lambda pos: pos.distance_to_closest(tumors)
                                          - pos.distance_to(
                                              self.enemy_start_locations[0]),
                                          reverse=True)
            else:
                valid_placements = sorted(valid_placements,
                                          key=lambda pos: pos.distance_to(
                                              self.enemy_start_locations[0]))
        if valid_placements:
            self.actions.append(unit(unit_ability, valid_placements[0]))
            if unit_ability == BUILD_CREEPTUMOR_TUMOR:  # if tumor
                self.used_tumors.append(unit.tag)

    async def queens_abilities(self):
        """Injection and creep spread"""
        queens = self.units(QUEEN)
        hatchery = self.townhalls
        for queen in queens.idle:
            selected = self.townhalls.closest_to(queen.position)
            if queen.energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                self.actions.append(queen(EFFECT_INJECTLARVA, selected))
            elif queen.energy > 26:
                await self.place_tumor(queen)
        for hatch in hatchery.ready.noqueue:
            if not queens.closer_than(8, hatch):
                for queen in queens:
                    if not self.townhalls.closer_than(8, queen).exists:
                        self.actions.append(queen.move(hatch.position))

    async def spread_creep(self):
        """ Iterate over all tumors to spread itself """
        tumors = self.units(CREEPTUMORQUEEN) \
                 | self.units(CREEPTUMOR) \
                 | self.units(CREEPTUMORBURROWED)
        for tumor in tumors:
            if tumor.tag not in self.used_tumors:
                await self.place_tumor(tumor)
