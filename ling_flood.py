import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.constants import HATCHERY, ZERGLING, QUEEN, LARVA, EFFECT_INJECTLARVA, \
SPAWNINGPOOL, RESEARCH_ZERGLINGMETABOLICBOOST, OVERLORD, EXTRACTOR, DRONE,\
QUEENSPAWNLARVATIMER, ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, ZERGLINGMOVEMENTSPEED,\
EVOLUTIONCHAMBER, RESEARCH_ZERGMELEEWEAPONSLEVEL1, RESEARCH_ZERGGROUNDARMORLEVEL1

from sc2.player import Bot, Computer

# TODO optimize everything

class EarlyAggro(sc2.BotAI):
    """It does an early aggression and tries to make a transition"""
    def __init__(self):
        self.flag1 = False
        self.flag2 = False
        self.actions = []

    async def on_step(self, iteration):
        self.actions = []
        await self.armor_attack()
        await self.build_evochamber()
        await self.build_extrator()
        await self.build_hatchery()
        await self.build_overlords()
        await self.build_queens_inject_larva()
        await self.build_spawning_pool()
        await self.build_workers()
        await self.build_zerglings()
        await self.defend_attack()
        await self.distribute_workers()
        await self.metabolic_boost()
        await self.do_actions(self.actions)

    async def armor_attack(self):
        """It researches attack and armor, maybe will need to be expanded later"""
        if self.units(EVOLUTIONCHAMBER).ready.idle.exists:
            for evo in self.units(EVOLUTIONCHAMBER).ready.idle:
                abilities = await self.get_available_abilities(evo)
                abilities_list = [RESEARCH_ZERGMELEEWEAPONSLEVEL1,
                                  RESEARCH_ZERGGROUNDARMORLEVEL1]
                for ability in abilities_list:
                    if ability in abilities:
                        if self.can_afford(ability):
                            self.actions.append(evo(ability))

    async def build_evochamber(self):
        """It builds evolution chambers, maybe can be brought earlier in the game"""
        if self.can_afford(EVOLUTIONCHAMBER) and self.townhalls.amount >= 3 \
                and not self.already_pending(EVOLUTIONCHAMBER) \
                and not self.units(EVOLUTIONCHAMBER).exists:
            await self.build(EVOLUTIONCHAMBER, near=self.units(SPAWNINGPOOL).first)

    async def build_extrator(self):
        """It builds extractors, maybe soon it will have to be expanded"""
        gas = self.units(EXTRACTOR)
        if self.townhalls.ready.exists:
            vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.ready.random)
            for gaiser in vgs:
                if not gas.exists and not self.already_pending(EXTRACTOR)\
                    and self.can_afford(EXTRACTOR)\
                    and self.units(HATCHERY).amount == 2:
                    drone = self.select_build_worker(gaiser.position)
                    self.actions.append(drone.build(EXTRACTOR, gaiser))
                    break

    async def build_hatchery(self):
        """It builds hatcheries, logic for third and more can be improved"""
        try:
            if self.can_afford(HATCHERY) and not self.already_pending(HATCHERY):
                if self.townhalls.amount < 2:
                    await self.expand_now()
                elif self.townhalls.amount == 2\
                        and self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) == 1:
                    await self.expand_now()
        except AssertionError:
            print("damn it")

    async def build_overlords(self):
        """It trains overlords maybe it can be improved for later stages
        and for earlier sometimes it creates much more than needed"""
        larva = self.units(LARVA)
        if self.supply_left < 4 and self.can_afford(OVERLORD) and larva.exists \
                and self.already_pending(OVERLORD) <= 2 and self.supply_cap != 200:
            self.actions.append(larva.random.train(OVERLORD))

    async def build_queens_inject_larva(self):
        """it builds queens and injects maybe later can be improving by adding queens
         for creep and transfusions"""
        queens = self.units(QUEEN)
        hatchery = self.units(HATCHERY)
        if hatchery.exists:
            hatcheries_random = self.units(HATCHERY).random
            if self.units(SPAWNINGPOOL).ready.exists:
                if queens.amount < hatchery.amount and hatcheries_random.is_ready \
                    and not self.already_pending(QUEEN)\
                    and hatcheries_random.noqueue and self.supply_left > 1:
                    if self.can_afford(QUEEN) and not queens.closer_than(8, hatcheries_random):
                        self.actions.append(hatcheries_random.train(QUEEN))
            for queen in queens.idle:
                selected = hatchery.closest_to(queen.position)
                if queen.energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                    self.actions.append(queen(EFFECT_INJECTLARVA, selected))

    async def build_spawning_pool(self):
        """It builds a spawning pool, no way to improve"""
        hatchery = self.units(HATCHERY)
        if self.can_afford(SPAWNINGPOOL) and not self.units(SPAWNINGPOOL).exists\
                and not self.already_pending(SPAWNINGPOOL) and hatchery.amount == 2:
            await self.build(SPAWNINGPOOL, near=hatchery.first.position.towards(self._game_info.map_center, 5))

    async def build_workers(self):
        """It builds workers, can be improved for the transition"""
        workers_total = self.workers.ready.amount
        larva = self.units(LARVA)
        hatchery = self.units(HATCHERY)
        if workers_total == 12 and larva.exists and not self.already_pending(DRONE):
            self.actions.append(larva.random.train(DRONE))
        elif workers_total in [13, 14, 15, 16] and self.can_afford(DRONE)\
            and self.supply_left > 0\
            and larva.closer_than(4, hatchery.first).exists\
            and self.units(OVERLORD).amount > 1:
            self.actions.append(larva.closer_than(4, hatchery.first).random.train(DRONE))
        elif self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) == 1\
                and workers_total < self.townhalls.amount * 14 \
                and larva.exists:
            self.actions.append(larva.random.train(DRONE))

    async def build_zerglings(self):
        """It trains zergling non-stop, can be improved"""
        larva = self.units(LARVA)
        if self.units(SPAWNINGPOOL).ready.exists and larva.amount != 1:
            if larva.exists and self.can_afford(ZERGLING) and self.supply_left > 0:
                self.actions.append(larva.random.train(ZERGLING))

    async def defend_attack(self):
        """It defends and attacks with zerglings, can be improved f.e-make the attack periodic,
           and stronger each time also make the units retreat less"""
        enemy_build = self.known_enemy_structures
        filtered_enemies = self.known_enemy_units.not_structure.exclude_type([ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA])
        good_health = self.units(ZERGLING).filter(lambda x: x.health > 32)
        bad_health = self.units(ZERGLING).filter(lambda x: x.health <= 9)
        target = filtered_enemies.not_flying
        zergl = self.units(ZERGLING)
        if self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) >= 0.7\
            and zergl.amount > 12:
            for zergling in good_health:
                if target.exists:
                    self.actions.append(zergling.attack(target.closest_to(zergling.position)))
                elif enemy_build.exists:
                    self.actions.append(zergling.attack(enemy_build.closest_to(zergling.position)))
                elif zergling.position.distance_to(self.enemy_start_locations[0]) > 0:
                    self.actions.append(zergling.attack(self.enemy_start_locations[0]))
        elif zergl.exists:
            for zergling in zergl:
                if filtered_enemies.closer_than(10, self.townhalls.random.position).exists:
                    if target.exists:
                        self.actions.append(zergling.attack(target.closest_to(zergling.position)))
            for zergling in bad_health:
                if target.closer_than(10, self._game_info.map_center).exists:
                    self.actions.append(zergling.attack(target.closest_to(zergling.position)))
                else:
                    self.actions.append(zergling.move(self._game_info.map_center))

    async def metabolic_boost(self):
        """It research zergling speed and distribute workers on and off gas, the former is good
        the latter can be improved"""
        pool = self.units(SPAWNINGPOOL)
        if pool.ready.idle.exists:
            if RESEARCH_ZERGLINGMETABOLICBOOST\
                in await self.get_available_abilities(pool.first):
                if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST):
                    self.actions.append(pool.first(RESEARCH_ZERGLINGMETABOLICBOOST))

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, EarlyAggro()),
    Computer(Race.Protoss, Difficulty.Hard)], realtime=False)
run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, EarlyAggro()),
    Computer(Race.Terran, Difficulty.Hard)], realtime=False)
run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, EarlyAggro()),
    Computer(Race.Zerg, Difficulty.Hard)], realtime=False)
