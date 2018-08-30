import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.constants import HATCHERY, ZERGLING, QUEEN, LARVA, EFFECT_INJECTLARVA, \
SPAWNINGPOOL, RESEARCH_ZERGLINGMETABOLICBOOST, OVERLORD, EXTRACTOR, DRONE,\
QUEENSPAWNLARVATIMER, ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, ZERGLINGMOVEMENTSPEED,\
EVOLUTIONCHAMBER, RESEARCH_ZERGMELEEWEAPONSLEVEL1, RESEARCH_ZERGGROUNDARMORLEVEL1,\
ZERGGROUNDARMORSLEVEL1, UPGRADETOLAIR_LAIR, RESEARCH_ZERGGROUNDARMORLEVEL2,\
RESEARCH_ZERGMELEEWEAPONSLEVEL2, SCV, PROBE, INFESTATIONPIT, HIVE, LAIR, UPGRADETOHIVE_HIVE,\
ZERGGROUNDARMORSLEVEL2, RESEARCH_ZERGMELEEWEAPONSLEVEL3, RESEARCH_ZERGGROUNDARMORLEVEL3,\
RESEARCH_ZERGLINGADRENALGLANDS, CANCEL_MORPHLAIR, CANCEL_MORPHHIVE,ULTRALISKCAVERN, ULTRALISK,\
RESEARCH_CHITINOUSPLATING

from sc2.player import Bot, Computer

# TODO rebuild LAIR or HIVE if it gets destroyed(test it)
# TODO add static defense into the priority targets
# TODO exclude infested terran from targets
# TODO better ultra cavern placement
# TODO ffs make it search for bases
# TODO add spine crawlers after first push(maybe)
# TODO replay analisys and improve the timings and values(better second wave of zerglings logic)
# TODO refactor and organize
# TODO dont follow the scouting worker ffs(3)
# TODO not keep attacking when ramp is blocked(3)
# TODO better vision spread(3)
# TODO make overlord when injecting(3)
# TODO some detection(3)
# TODO add GGlords(3)
# TODO 3rd expansion should be earlier(3)

class EarlyAggro(sc2.BotAI):
    """It does an early aggression and tries to make a transition"""
    def __init__(self):
        self.flag1 = False
        self.flag2 = False
        self.flag3 = False
        self.flag4 = False
        self.actions = []
        self.close_enemies = []

    async def on_step(self, iteration):
        self.close_enemies = []
        self.actions = []
        await self.armor_attack()
        await self.build_evochamber()
        await self.build_extrator()
        await self.build_hatchery()
        await self.build_infestation_pit()
        await self.build_overlords()
        await self.build_queens_inject_larva()
        await self.build_spawning_pool()
        await self.build_workers()
        await self.build_zerglings()
        await self.chitinous_plating()
        await self.defend_attack()
        await self.defend_worker_rush()
        await self.distribute_workers()
        await self.build_ultralisk()
        await self.build_ultralisk_cavern()
        await self.make_hive()
        await self.make_lair()
        await self.metabolic_boost()
        await self.do_actions(self.actions)

    async def armor_attack(self):
        """It researches attack and armor, maybe will need to be expanded later"""
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
        """It builds evolution chambers, maybe can be brought earlier in the game"""
        evochamber = self.units(EVOLUTIONCHAMBER)
        pool = self.units(SPAWNINGPOOL)
        if self.can_afford(EVOLUTIONCHAMBER) and self.townhalls.amount >= 3 \
                and evochamber.amount < 2 and pool.exists and not self.already_pending(EVOLUTIONCHAMBER):
            await self.build(EVOLUTIONCHAMBER, near=pool.first.position.towards(self._game_info.map_center, 3))

    async def build_extrator(self):
        """It builds extractors, maybe soon it will have to be expanded"""
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
        """It builds hatcheries, logic for third and more can be improved"""
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
        if self.already_pending(ZERGGROUNDARMORSLEVEL2) > 0.1 and self.can_afford(INFESTATIONPIT)\
            and self.townhalls.exists and not self.already_pending(INFESTATIONPIT)\
            and not self.units(INFESTATIONPIT).exists and self.units(LAIR).ready.exists\
            and self.units(ZERGLING).amount > 15:
            await self.build(INFESTATIONPIT, near=self.units(EVOLUTIONCHAMBER).first.position)

    async def build_overlords(self):
        """It trains overlords maybe it can be improved for later stages
        and for earlier sometimes it creates much more than needed"""
        larva = self.units(LARVA)
        if self.can_afford(OVERLORD) and larva.exists and self.supply_left < 5 \
                and self.supply_cap != 200:
            if self.townhalls.amount == 1:
                if not self.already_pending(OVERLORD):
                    self.actions.append(larva.random.train(OVERLORD))
            elif self.already_pending(OVERLORD) <= 2:
                self.actions.append(larva.random.train(OVERLORD))

    async def build_queens_inject_larva(self):
        """it builds queens and injects maybe later can be improving by adding queens
         for creep and transfusions"""
        queens = self.units(QUEEN)
        hatchery = self.units(HATCHERY)
        if hatchery.exists:
            hatcheries_random = self.townhalls.random
            if self.units(SPAWNINGPOOL).ready.exists:
                if queens.amount < hatchery.amount and hatcheries_random.is_ready \
                    and not self.already_pending(QUEEN)\
                    and hatcheries_random.noqueue and self.supply_left > 1:
                    if self.can_afford(QUEEN) and not queens.closer_than(8, hatcheries_random):
                        self.actions.append(hatcheries_random.train(QUEEN))
            for queen in queens.idle:
                selected = self.townhalls.closest_to(queen.position)
                if queen.energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                    self.actions.append(queen(EFFECT_INJECTLARVA, selected))

    async def build_spawning_pool(self):
        """It builds a spawning pool, no way to improve"""
        hatchery = self.units(HATCHERY)
        if self.can_afford(SPAWNINGPOOL) and not self.units(SPAWNINGPOOL).exists\
        and not self.already_pending(SPAWNINGPOOL) and hatchery.amount == 2:
            await self.build(SPAWNINGPOOL, near=hatchery.first.position.towards(self._game_info.map_center, 5))

    async def build_ultralisk(self):
        if self.units(ULTRALISKCAVERN).ready.exists:
            if self.units(LARVA).exists and self.can_afford(ULTRALISK) and self.supply_left > 5:
                self.actions.append(self.units(LARVA).random.train(ULTRALISK))

    async def build_ultralisk_cavern(self):
        if self.units(HIVE).exists and self.can_afford(ULTRALISKCAVERN)\
        and not self.already_pending(ULTRALISKCAVERN) and not self.units(ULTRALISKCAVERN).exists:
            await self.build(ULTRALISKCAVERN, near=self.units(INFESTATIONPIT).first.position)

    async def build_workers(self):
        """It builds workers, can be improved for the transition"""
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
            elif workers_total in [13, 14, 15] and self.can_afford(DRONE)\
                and self.supply_left > 0\
                and larva.closer_than(4, hatchery.first).exists\
                and self.units(OVERLORD).amount + self.already_pending(OVERLORD) > 1:
                if workers_total == 15:
                    if self.units(EXTRACTOR).exists and self.units(SPAWNINGPOOL).exists:
                        self.actions.append(larva.random.train(DRONE))
                else:
                    self.actions.append(larva.random.train(DRONE))
            elif self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) == 1\
                and workers_total < self.townhalls.amount * 16 \
                and larva.exists and workers_total < 86\
                    and self.units(ZERGLING).amount >= 13.5:
                self.actions.append(larva.random.train(DRONE))

    async def build_zerglings(self):
        """It trains zergling non-stop, can be improved"""
        larva = self.units(LARVA)
        if self.units(SPAWNINGPOOL).ready.exists:
            if larva.exists and self.can_afford(ZERGLING) and self.supply_left > 0:
                if self.units(ULTRALISKCAVERN).ready.exists:
                    if self.units(ULTRALISK).amount * 14 > self.units(ZERGLING).amount:
                        self.actions.append(larva.random.train(ZERGLING))
                else:
                    self.actions.append(larva.random.train(ZERGLING))

    async def chitinous_plating(self):
        cavern = self.units(ULTRALISKCAVERN)
        if cavern.ready.exists:
            available_research = await self.get_available_abilities(cavern.ready.first)
            if RESEARCH_CHITINOUSPLATING in available_research\
                and self.can_afford(RESEARCH_CHITINOUSPLATING):
                self.actions.append(cavern.first(RESEARCH_CHITINOUSPLATING))

    async def defend_attack(self):
        """It defends and attacks with zerglings, can be improved f.e-make the attack periodic,
           and stronger each time also make the units retreat less"""
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
        abilities = await self.get_available_abilities(homecity)
        morphs = [CANCEL_MORPHLAIR, CANCEL_MORPHHIVE]
        for m in morphs:
            if m in abilities:
                return True
        return False

    async def make_hive(self):
        if self.units(INFESTATIONPIT).ready.exists and not self.units(HIVE).exists\
            and self.can_afford(HIVE) and not any([await self.is_morphing(h) for h in self.units(LAIR)]) \
            and self.units(ZERGLING).amount > 15 and self.units(LAIR).ready.idle.exists:
            self.actions.append(self.units(LAIR).ready.idle.first(UPGRADETOHIVE_HIVE))

    async def make_lair(self):
        if self.townhalls.amount >= 4 and self.can_afford(UPGRADETOLAIR_LAIR)\
            and not (self.units(LAIR).exists or self.units(HIVE).exists)\
            and not any([await self.is_morphing(h) for h in self.units(HATCHERY)]):
            self.actions.append(self.units(HATCHERY).ready.idle.first(UPGRADETOLAIR_LAIR))

    async def metabolic_boost(self):
        """It research zergling speed and distribute workers on and off gas, the former is good
        the latter can be improved"""
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
