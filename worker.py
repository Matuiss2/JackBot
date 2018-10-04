"""Everything related to workers behavior goes here"""
import heapq

from sc2.constants import DRONE, EXTRACTOR, HATCHERY, HIVE, LAIR, PROBE, SCV, ZERGLINGMOVEMENTSPEED


class worker_control:
    def __init__(self):
        self.defense_mode = False
        self.defenders = None
        self.defender_tags = None
        self.collect_gas_for_speedling = False

    async def split_workers(self):
        """Split the workers on the beginning """
        for drone in self.drones:
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        lowesthp = min(enemy.health for enemy in enemies)
        low_enemies = enemies.filter(lambda x: x.health == lowesthp)
        target = low_enemies.closest_to(unit)
        self.actions.append(unit.attack(target))

    async def defend_worker_rush(self):
        """It destroys every worker rush without losing more than 2 workers,
         it counter scouting worker rightfully now, its too big and can be split"""
        base = self.units(HATCHERY).ready
        if base:
            enemy_units_close = self.known_enemy_units.closer_than(8, base.first).of_type([PROBE, DRONE, SCV])
            if enemy_units_close and not self.defense_mode:
                self.defense_mode = True
                highest_hp_drones = heapq.nlargest(
                    2 * (len(enemy_units_close)), self.drones.collecting, key=lambda drones: drones.health
                )
                self.defender_tags = [unit.tag for unit in highest_hp_drones]
            if self.defense_mode and not enemy_units_close:
                if self.defenders:
                    for drone in self.defenders:
                        self.actions.append(drone.gather(self.state.mineral_field.closest_to(base.first)))
                        continue
                    self.defenders = None
                    self.defender_tags = []
                self.defense_mode = False
                self.defender_tags = []
                self.defenders = None
            if self.defense_mode and enemy_units_close:
                self.defenders = self.drones.filter(
                    lambda worker: worker.tag in self.defender_tags and worker.health > 0
                )
                defender_deficit = min(len(self.drones) - 1, 2 * len(enemy_units_close)) - len(self.defenders)
                if defender_deficit > 0:
                    highest_hp_additional_drones = heapq.nlargest(
                        defender_deficit, self.drones.collecting, key=lambda drones: drones.health
                    )
                    additional_drones = [unit.tag for unit in highest_hp_additional_drones]
                    self.defender_tags = self.defender_tags + additional_drones
                for drone in self.defenders:
                    # 6 hp is the lowest you can take a hit and still survive
                    if drone.health <= 6:
                        if not drone.is_collecting:
                            mineral_field = self.state.mineral_field.closest_to(base.first.position)
                            self.actions.append(drone.gather(mineral_field))
                            continue
                        else:
                            self.defender_tags.remove(drone.tag)
                    else:
                        if drone.weapon_cooldown <= 0.60:
                            targets_close = enemy_units_close.in_attack_range_of(drone)
                            if targets_close:
                                self.attack_lowhp(drone, targets_close)
                                continue
                            else:
                                target = enemy_units_close.closest_to(drone)
                                if target:
                                    self.actions.append(drone.attack(target))
                                    continue
                        else:
                            targets_in_range_1 = enemy_units_close.closer_than(1, drone)
                            if targets_in_range_1:
                                lowest_hp_enemy = min(targets_in_range_1, key=(lambda x: x.health + x.shield))
                                self.actions.append(drone.move(lowest_hp_enemy))
                                continue
                            else:
                                lowest_hp_enemy = min(enemy_units_close, key=(lambda x: x.health + x.shield))
                                self.actions.append(drone.move(lowest_hp_enemy))
                                continue

    async def distribute_drones(self):
        mining_bases = self.units.of_type({HATCHERY, LAIR, HIVE}).ready.filter(lambda base: base.ideal_harvesters > 0)
        mineral_fields = self.mineral_fields_of(mining_bases)
        mining_places = mining_bases | self.units(EXTRACTOR).ready

        self.gather_gas()

        deficit_bases, workers_to_distribute = self.calculate_distribution(mining_places)

        if not deficit_bases:
            for drone in self.drones.idle:
                if mineral_fields:
                    mf = mineral_fields.closest_to(drone)
                    self.actions.append(drone.gather(mf))
            return

        self.distribute_to_deficits(mining_bases, workers_to_distribute, mineral_fields, deficit_bases)

    def calculate_distribution(self, mining_bases):
        workers_to_distribute = [drone for drone in self.drones.idle]
        mineral_tags = {mf.tag for mf in self.state.mineral_field}
        mining_places = mining_bases | self.units(EXTRACTOR).ready
        extractor_tags = {ref.tag for ref in self.units(EXTRACTOR)}
        deficit_bases = []

        for mining_place in mining_places:
            difference = mining_place.surplus_harvesters
            if difference > 0:
                for _ in range(difference):
                    if mining_place.name == "Extractor":
                        moving_drone = self.drones.filter(
                            lambda x: x.order_target in extractor_tags and x not in workers_to_distribute
                        )
                    else:
                        moving_drone = self.drones.filter(
                            lambda x: x.order_target in mineral_tags and x not in workers_to_distribute
                        )
                    if moving_drone:
                        workers_to_distribute.append(moving_drone.closest_to(mining_place))
            elif difference < 0:
                deficit_bases.append([mining_place, difference])

        return deficit_bases, workers_to_distribute

    def mineral_fields_deficit(self, mineral_fields, deficit_bases):
        if deficit_bases:
            worker_order_targets = {worker.order_target for worker in self.drones.collecting}
            mineral_fields_deficit = [mf for mf in mineral_fields.closer_than(8, deficit_bases[0][0])]
            return sorted(
                mineral_fields_deficit,
                key=lambda mineral_field: (
                    mineral_field.tag not in worker_order_targets,
                    mineral_field.mineral_contents,
                ),
            )
        return []

    def distribute_to_deficits(self, mining_bases, workers_to_distribute, mineral_fields, deficit_bases):

        deficit_bases = [x for x in deficit_bases if x[0].type_id != EXTRACTOR]

        if deficit_bases and workers_to_distribute:
            mineral_fields_deficit = self.mineral_fields_deficit(mineral_fields, deficit_bases)

            deficit_extractors = [x for x in deficit_bases if x[0].type_id == EXTRACTOR]

            for worker in workers_to_distribute:
                if mining_bases and deficit_bases and mineral_fields_deficit:
                    self.distribute_to_mineral_field(mineral_fields_deficit, worker, deficit_bases)
                if self.distribute_to_extractors(deficit_extractors):
                    self.distribute_to_extractor(deficit_extractors, worker)

    def distribute_to_extractors(self, deficit_extractors):
        return self.units(EXTRACTOR).ready and deficit_extractors and self.require_gas

    def distribute_to_extractor(self, deficit_extractors, worker):
        self.actions.append(worker.gather(deficit_extractors[0][0]))
        deficit_extractors[0][1] += 1
        if deficit_extractors[0][1] == 0:
            del deficit_extractors[0]

    def distribute_to_mineral_field(self, mineral_fields_deficit, worker, deficit_bases):
        drone_target = mineral_fields_deficit[0]
        if len(mineral_fields_deficit) >= 2:
            del mineral_fields_deficit[0]
        self.actions.append(worker.gather(drone_target))
        deficit_bases[0][1] += 1
        if deficit_bases[0][1] == 0:
            del deficit_bases[0]

    def gather_gas(self):
        if self.require_gas:
            for extractor in self.units(EXTRACTOR):
                required_drones = extractor.ideal_harvesters - extractor.assigned_harvesters
                if required_drones > 0 and required_drones < self.drones.amount:
                    for drone in self.drones.random_group_of(required_drones):
                        self.actions.append(drone.gather(extractor))

    @property
    def require_gas(self):
        return self.require_gas_for_speedlings or self.vespene < self.minerals

    @property
    def require_gas_for_speedlings(self):
        return not self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED) and self.vespene < 100

    def mineral_fields_of(self, bases):
        return self.state.mineral_field.filter(
            lambda field: any([field.distance_to(base) <= 8 for base in bases])
        )
