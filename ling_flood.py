import sc2
import math
from sc2 import run_game, maps, Race, Difficulty
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.player import Bot, Computer
from sc2.data import ActionResult

# TODO add static defense into the priority targets
# TODO exclude infested terran from targets
# TODO better ultra cavern placement
# TODO make it search for bases when starting base is already destroyed
# TODO add spine crawlers after first push(maybe)
# TODO improve the timings and values(better second wave of zerglings logic)
# TODO refactor and organize the code
# TODO dont follow the scouting worker all the way(3)
# TODO not keep attacking when ramp is blocked or when its an impossible fight(3)
# TODO better vision spread(3)
# TODO add some detection(3)
# TODO add Broodlords(3)
# TODO 3rd expansion should be earlier(3)
# TODO creepy spread implementation (will have to modify queen injection logic probably)

class EarlyAggro(sc2.BotAI):
    def __init__(self):
        self.flag2 = False
        self.flag3 = False
        self.actions = []
        self.close_enemies = []
        self.base_queen_relation = {}

    async def on_step(self, iteration):
        self.close_enemies = []
        self.actions = []
        await self.armor_attack()
        await self.build_evochamber()
        await self.build_extrator()
        await self.build_hatchery()
        await self.build_infestation_pit()
        await self.build_queens_inject_larva()
        await self.spread_creep()
        await self.build_spawning_pool()

        await self.build_units()

        await self.chitinous_plating()
        await self.defend_attack()
        await self.defend_worker_rush()
        await self.distribute_workers()
        await self.build_ultralisk_cavern()
        await self.make_hive()
        await self.make_lair()
        await self.metabolic_boost()
        await self.do_actions(self.actions)

    async def build_units(self):
        """ Build one unit, the most prioritized at the moment """

        if not self.units(LARVA).exists:
            return

        available_units_in_order = [
            self.build_overlords, 
            self.build_workers, 
            self.build_zerglings, 
            self.build_ultralisk
            ]

        for build_unit_function in available_units_in_order:
            """ The function returns if it wants to build the unit and might build it """
            want_to_built_unit = await build_unit_function()
            if want_to_built_unit:
                break

    async def armor_attack(self):
        """all land upgrades, it works as intended maybe some optimizations are possible"""
        evochamber = self.units(EVOLUTIONCHAMBER)
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

    async def build_evochamber(self):
        """It builds the evochamber, its probable that its timing is not right"""
        evochamber = self.units(EVOLUTIONCHAMBER)
        pool = self.units(SPAWNINGPOOL)
        if self.can_afford(EVOLUTIONCHAMBER) and self.townhalls.amount >= 3 \
                and evochamber.amount < 2 and pool.exists and not self.already_pending(EVOLUTIONCHAMBER):
            await self.build(EVOLUTIONCHAMBER, near=pool.first.position.towards(self._game_info.map_center, 3))

    async def build_extrator(self):
        """Couldnt find another way to build the gaisers its way to inefficient
         and sometimes throws errors when attacked timing can be improved also"""
        gas = self.units(EXTRACTOR)
        if self.townhalls.ready.exists:
            vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.ready.random)
            for gaiser in vgs:
                if not self.already_pending(EXTRACTOR) and self.can_afford(EXTRACTOR):
                    if not gas.exists and self.units(HATCHERY).amount == 2:
                        drone = self.select_build_worker(gaiser.position)
                        self.actions.append(drone.build(EXTRACTOR, gaiser))
                        break
                    elif self.units(INFESTATIONPIT).exists:
                        if self.units(INFESTATIONPIT).first.build_progress > 0.2\
                        and gas.amount < 7:
                            drone = self.select_build_worker(gaiser.position)
                            self.actions.append(drone.build(EXTRACTOR, gaiser))
                            break

    async def build_hatchery(self):
        """The third base is placed very slow, the try except wont be needed
         when updated to next library version"""
        try:
            for hacth in self.townhalls:
                enemies = self.known_enemy_units.not_structure.closer_than(35, hacth.position).exclude_type([DRONE, SCV, PROBE])
                if len(enemies) > 0:
                    self.close_enemies.append(1)
            if self.minerals > 175 and self.townhalls.amount < 2 and not self.flag3:
                self.flag3 = True
                self.actions.append(self.workers.first.move(await self.get_next_expansion()))
            if self.can_afford(HATCHERY) and not self.already_pending(HATCHERY)\
                and len(self.close_enemies) == 0:
                if self.townhalls.amount < 3:
                    await self.expand_now()
                elif self.townhalls.amount >= 3\
                    and self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL1) > 0.3:
                    await self.expand_now()
        except AssertionError:
            print("damn it")

    async def build_infestation_pit(self):
        """Good enough for now, but some conditions can probably be changed"""
        if self.already_pending(ZERGGROUNDARMORSLEVEL2) > 0.1 and self.can_afford(INFESTATIONPIT)\
            and self.townhalls.exists and not self.already_pending(INFESTATIONPIT)\
            and not self.units(INFESTATIONPIT).exists and self.units(LAIR).ready.exists\
            and self.units(ZERGLING).amount > 15:
            await self.build(INFESTATIONPIT, near=self.units(EVOLUTIONCHAMBER).first.position)

    async def build_overlords(self):
        """We do not get supply blocked, but builds one more overlord that needed at some points"""
        larva = self.units(LARVA)
        if self.supply_left < 5 and not self.supply_cap >= 200:
            if self.can_afford(OVERLORD) and larva.exists:
                if self.townhalls.amount == 1 and self.already_pending(OVERLORD):
                    return False
                elif self.already_pending(OVERLORD) >= 2: # Don't make more than two at once
                    return False

                self.actions.append(larva.random.train(OVERLORD))
                return True
                
        return False

    async def build_queens_inject_larva(self):
        """ Assigns a queen per base and always have one queen to spread creep """
        queens = self.units(QUEEN)
        bases = self.units(HATCHERY) | self.units(LAIR) | self.units(HIVE)

        # Handle injection
        for base in bases:
            if base.tag in self.base_queen_relation:
                queen = self.base_queen_relation[base.tag]

                if not queen: # If queen is dead
                    del self.base_queen_relation[base.tag]

                if queen.energy >= 25 and not base.has_buff(QUEENSPAWNLARVATIMER):
                    self.actions.append(queen(EFFECT_INJECTLARVA, base))

        queen_with_no_base = queens.filter(lambda queen: queen.tag not in map(lambda unit: unit.tag, self.base_queen_relation.values()))
        base_with_no_queen = bases.filter(lambda base: base.tag not in self.base_queen_relation.keys())

        # Match queens to bases
        for queen in queen_with_no_base:
            if base_with_no_queen.exists:
                base = base_with_no_queen.closest_to(queen)
                self.base_queen_relation[base.tag] = queen_with_no_base.closest_to(base)
                return # Make sure we don't overwrite
            else:
                #Spread creep
                if queen.is_idle and queen.energy >= 25:
                    await self.place_tumor(queen)

        # Make more queens if needed
        if 1 + base_with_no_queen.amount > queen_with_no_base.amount + self.already_pending(QUEEN):
            base = base_with_no_queen.noqueue 

            if not base.exists and bases.amount > 1:
                base = bases.noqueue

            if base.exists and self.can_afford(QUEEN) and self.supply_left > 2:
                    self.actions.append(base.random.train(QUEEN))

    async def spread_creep(self):
        """ Itereate over all tumors to spread itself """
        tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)
        for tumor in tumors:
            await self.place_tumor(tumor)


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
        locationAttempts = 30
        spreadDistance = 8
        location = unit.position

        # Define random positions around unit
        positions = [Point2((location.x + spreadDistance * math.cos(math.pi * alpha * 2 / locationAttempts), location.y + spreadDistance * math.sin(math.pi * alpha * 2 / locationAttempts))) for alpha in range(locationAttempts)]
        # check if any of the positions are valid
        validPlacements = await self._client.query_building_placement(ability, positions)
        # filter valid results
        validPlacements = [p for index, p in enumerate(positions) if validPlacements[index] == ActionResult.Success]
        # now "validPlacements" will contain a list of points where it is possible to place creep tumors
        # of course creep tumors have a limited range to place creep tumors but queens can move anywhere
        if validPlacements:
            tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)
            if tumors.amount:
                validPlacements = sorted(validPlacements, key=lambda pos: pos.distance_to_closest(tumors) - pos.distance_to(self._game_info.map_center), reverse=True)
            else:
                validPlacements = sorted(validPlacements, key=lambda pos: pos.distance_to(self._game_info.map_center))

            for location in validPlacements:
                err = await self.do(unit(unit_ability, location))
                if not err:
                    break

    async def build_spawning_pool(self):
        """Good enough for now, maybe the logic will need to be changed
         when rush defenses get implemented"""
        hatchery = self.units(HATCHERY)
        if self.can_afford(SPAWNINGPOOL) and not self.units(SPAWNINGPOOL).exists\
        and not self.already_pending(SPAWNINGPOOL) and hatchery.amount == 2:
            await self.build(SPAWNINGPOOL, near=hatchery.first.position.towards(self._game_info.map_center, 5))

    async def build_ultralisk(self):
        """Good for now but it might need to be changed vs particular
         enemy units compositions"""
        if self.units(ULTRALISKCAVERN).ready.exists:
            if self.units(LARVA).exists and self.can_afford(ULTRALISK) and self.supply_left > 5:
                self.actions.append(self.units(LARVA).random.train(ULTRALISK))
                return True
        return False

    async def build_ultralisk_cavern(self):
        """Placement need to be improved, also it might need to be changed vs particular
         enemy units compositions, vs only flying units, this don't need to be built"""
        if self.units(HIVE).exists and self.can_afford(ULTRALISKCAVERN)\
        and not self.already_pending(ULTRALISKCAVERN) and not self.units(ULTRALISKCAVERN).exists:
            await self.build(ULTRALISKCAVERN, near=self.units(INFESTATIONPIT).first.position)

    async def build_workers(self):
        """Good for the beginning, but it doesnt adapt to losses of drones very well"""
        workers_total = self.workers.amount
        larva = self.units(LARVA)
        hatchery = self.units(HATCHERY)
        for hacth in self.townhalls:
            enemies = self.known_enemy_units.not_structure.closer_than(35, hacth.position).exclude_type(
                [DRONE, SCV, PROBE])
            if len(enemies) > 0:
                self.close_enemies.append(1)
        if len(self.close_enemies) == 0:
            if workers_total == 12 and larva.exists and not self.already_pending(DRONE):
                self.actions.append(larva.random.train(DRONE))
                return True
            elif workers_total in [13, 14, 15] and self.can_afford(DRONE)\
                and self.supply_left > 0\
                and larva.closer_than(4, hatchery.first).exists\
                and self.units(OVERLORD).amount + self.already_pending(OVERLORD) > 1:
                if workers_total == 15:
                    if self.units(EXTRACTOR).exists and self.units(SPAWNINGPOOL).exists:
                        self.actions.append(larva.random.train(DRONE))
                        return True
                else:
                    self.actions.append(larva.random.train(DRONE))
                    return True
            elif self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) == 1\
                and workers_total < self.townhalls.amount * 16 \
                and larva.exists and workers_total < 86\
                    and self.units(ZERGLING).amount >= 13.5:
                self.actions.append(larva.random.train(DRONE))
                return True
        return False

    async def build_zerglings(self):
        """Needs to be improved so it doesnt block other units(this always get prioritized)"""
        larva = self.units(LARVA)
        if self.units(SPAWNINGPOOL).ready.exists:
            if larva.exists and self.can_afford(ZERGLING) and self.supply_left > 0:
                if self.units(ULTRALISKCAVERN).ready.exists:
                    if self.units(ULTRALISK).amount * 14 > self.units(ZERGLING).amount:
                        self.actions.append(larva.random.train(ZERGLING))
                        return True
                else:
                    self.actions.append(larva.random.train(ZERGLING))
                    return True
        return False

    async def chitinous_plating(self):
        """Just like armor_attack, it works perfectly but maybe it can be optimized"""
        cavern = self.units(ULTRALISKCAVERN)
        if cavern.ready.exists:
            available_research = await self.get_available_abilities(cavern.ready.first)
            if RESEARCH_CHITINOUSPLATING in available_research\
                and self.can_afford(RESEARCH_CHITINOUSPLATING):
                self.actions.append(cavern.first(RESEARCH_CHITINOUSPLATING))

    async def defend_attack(self):
        """Micro function, its just slight better than a-move, need A LOT of improvements"""
        enemy_build = self.known_enemy_structures
        filtered_enemies = self.known_enemy_units.not_structure.exclude_type([ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA])
        '''
        good_health = [z for z in self.units(ZERGLING) if z.health > 10]
        bad_health = (zb for zb in self.units(ZERGLING) if zb.health <= 9)
        '''
        target = filtered_enemies.not_flying
        zergl = self.units(ZERGLING)
        if zergl.exists:
            for zergling in zergl + self.units(ULTRALISK):
                if target.closer_than(17, zergling.position).exists:
                    self.actions.append(zergling.attack(target.closest_to(zergling.position)))
                elif enemy_build.closer_than(35, zergling.position).exists:
                    self.actions.append(zergling.attack(enemy_build.closest_to(zergling.position)))
                elif zergl.amount < 23:
                    self.actions.append(zergling.move(self._game_info.map_center.towards(self.enemy_start_locations[0], 11)))
                elif zergling.position.distance_to(self.enemy_start_locations[0]) > 0 and zergl.amount > 23:
                    self.actions.append(zergling.attack(self.enemy_start_locations[0]))
        '''
        elif zergl.exists:
            for zergling in zergl:
                if self.townhalls.exists:
                    if filtered_enemies.closer_than(10, self.townhalls.random.position).exists:
                        if target.exists:
                            self.actions.append(zergling.attack(target.closest_to(zergling.position)))
            for zergling in bad_health:
                if target.closer_than(10, self.units(HATCHERY).closest_to(zergling.position)).exists:
                    self.actions.append(zergling.attack(target.closest_to(zergling.position)))
                else:
                    if self.units(HATCHERY).exists:
                        self.actions.append(zergling.move(self.units(HATCHERY).closest_to(zergling.position)))'''

    async def defend_worker_rush(self):
        """Its the way I found to defend simple worker rushes,
         I don't know if it beats complexes worker rushes like tyr's bot,
        also it follows scouting workers all the way"""
        if self.known_enemy_units.exists and self.units(HATCHERY).exists:
            enemy_units_close = self.known_enemy_units.closer_than(5, self.units(HATCHERY).first).of_type([PROBE, DRONE, SCV])
            if enemy_units_close.exists and self.townhalls.amount < 2:
                selected_worker = self.workers.first
                if len(enemy_units_close) == 1:
                    self.actions.append(selected_worker.attack(self.known_enemy_units.closest_to(selected_worker.position)))
                else:
                    for worker in self.workers:
                        self.actions.append(worker.attack(self.known_enemy_units.closest_to(worker.position)))

    async def is_morphing(self, homecity):
        """Check if a base is morphing, good enough for now"""
        abilities = await self.get_available_abilities(homecity)
        morphs = [CANCEL_MORPHLAIR, CANCEL_MORPHHIVE]
        for m in morphs:
            if m in abilities:
                return True
        return False

    async def make_hive(self):
        """Works well, maybe the timing can be improved"""
        if self.units(INFESTATIONPIT).ready.exists and not self.units(HIVE).exists\
            and self.can_afford(HIVE) and not any([await self.is_morphing(h) for h in self.units(LAIR)]) \
            and self.units(ZERGLING).amount > 15 and self.units(LAIR).ready.idle.exists:
            self.actions.append(self.units(LAIR).ready.idle.first(UPGRADETOHIVE_HIVE))

    async def make_lair(self):
        """Good enough for now"""
        if self.townhalls.amount >= 4 and self.can_afford(UPGRADETOLAIR_LAIR)\
            and not (self.units(LAIR).exists or self.units(HIVE).exists)\
            and not any([await self.is_morphing(h) for h in self.units(HATCHERY)]):
            self.actions.append(self.units(HATCHERY).ready.idle.first(UPGRADETOLAIR_LAIR))

    async def metabolic_boost(self):
        """It sends 3 drones at the beginning to the extractor so it
         immediately research metabolic boost when ready, but I don't know
          how to take then off it right after needs improvement"""
        if self.units(EXTRACTOR).ready.exists and not self.flag2:
            self.flag2 = True
            extractor = self.units(EXTRACTOR).first
            for drone in self.workers.random_group_of(3):
                self.actions.append(drone.gather(extractor))
        pool = self.units(SPAWNINGPOOL)
        if pool.ready.idle.exists:
            available_research = await self.get_available_abilities(pool.first)
            research_list = [RESEARCH_ZERGLINGMETABOLICBOOST, RESEARCH_ZERGLINGADRENALGLANDS]
            for research in research_list:
                if research in available_research and self.can_afford(research):
                    self.actions.append(pool.first(research))
