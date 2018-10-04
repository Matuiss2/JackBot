"""Everything related to workers behavior goes here"""
import heapq

from sc2.constants import DRONE, EXTRACTOR, HATCHERY, HIVE, LAIR, PROBE, SCV, ZERGLINGMOVEMENTSPEED


class worker_control:
    def __init__(self):
        self.defenders = None
        self.defender_tags = None
        self.collect_gas_for_speedling = False

    async def split_workers(self):
        """Split the workers on the beginning """
        for drone in self.drones:
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))

    def lowest_hp(self, units):
        lowesthp = min(unit.health for unit in units)
        low_enemies = units.filter(lambda x: x.health == lowesthp)
        return low_enemies

    def closest_lowest_hp(self, unit, units):
        lowest_unit = self.lowest_hp(units)
        return lowest_unit.closest_to(unit)

    def move_lowhp(self, unit, enemies):
        """Move to enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.actions.append(unit.move(target))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.actions.append(unit.attack(target))

    async def defend_worker_rush(self):
        """It destroys every worker rush without losing more than 2 workers,
         it counter scouting worker rightfully now, its too big and can be split"""
        base = self.units(HATCHERY).ready
        if base:
            enemy_units_close = self.known_enemy_units.closer_than(8, base.first).of_type([PROBE, DRONE, SCV])

            if enemy_units_close and not self.defender_tags:
                self.build_defense_force(len(enemy_units_close))

            if self.defender_tags and not enemy_units_close:
                self.clear_defense_force(base)

            if self.defender_tags and enemy_units_close:
                self.refill_defense_force(len(enemy_units_close))

                for drone in self.defenders:
                    # 6 hp is the lowest you can take a hit and still survive
                    if not self.save_lowhp_drone(drone, base):
                        if drone.weapon_cooldown <= 0.60:
                            targets_close = enemy_units_close.in_attack_range_of(drone)
                            if targets_close:
                                self.attack_lowhp(drone, targets_close)
                            else:
                                target = enemy_units_close.closest_to(drone)
                                if target:
                                    self.actions.append(drone.attack(target))
                        else:
                            targets_in_range_1 = enemy_units_close.closer_than(1, drone)
                            if targets_in_range_1:
                                self.move_lowhp(drone, targets_in_range_1)
                            else:
                                self.move_lowhp(drone, enemy_units_close)

    def save_lowhp_drone(self, drone, base):
        if drone.health <= 6:
            if not drone.is_collecting:
                mineral_field = self.state.mineral_field.closest_to(base.first.position)
                self.actions.append(drone.gather(mineral_field))
            else:
                self.defender_tags.remove(drone.tag)
            return True
        return False

    def build_defense_force(self, enemy_count):
        self.defender_tags = self.defense_force(2 * enemy_count)

    def refill_defense_force(self, enemy_count):
        self.defenders = self.drones.filter(
            lambda worker: worker.tag in self.defender_tags and worker.health > 0
        )
        defender_deficit = self.calculate_defender_deficit(enemy_count)

        if defender_deficit > 0:
            additional_drones = self.defense_force(defender_deficit)
            self.defender_tags = self.defender_tags + additional_drones

    def clear_defense_force(self, base):
        if self.defenders:
            for drone in self.defenders:
                self.actions.append(drone.gather(self.state.mineral_field.closest_to(base.first)))
                continue
        self.defender_tags = []
        self.defenders = None

    def defense_force(self, count):
        highest_hp_drones = self.highest_hp_drones(count)
        return [unit.tag for unit in highest_hp_drones]

    def highest_hp_drones(self, count):
        return heapq.nlargest(count, self.drones.collecting, key=lambda drones: drones.health)

    def calculate_defender_deficit(self, enemy_count):
        return min(len(self.drones) - 1, 2 * enemy_count) - len(self.defenders)

    async def distribute_drones(self):
        mining_bases = self.units.of_type({HATCHERY, LAIR, HIVE}).ready.filter(lambda base: base.ideal_harvesters > 0)
        mineral_fields = self.mineral_fields_of(mining_bases)
        mining_places = mining_bases | self.units(EXTRACTOR).ready

        self.distribute_gas()

        deficit_bases, workers_to_distribute = self.calculate_distribution(mining_places)

        if not deficit_bases:
            for drone in self.drones.idle:
                if mineral_fields:
                    mf = mineral_fields.closest_to(drone)
                    self.actions.append(drone.gather(mf))
            return

        if workers_to_distribute:
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
        mineral_fields_deficit = self.mineral_fields_deficit(mineral_fields, deficit_bases)

        deficit_extractors = [x for x in deficit_bases if x[0].type_id == EXTRACTOR]
        for worker in workers_to_distribute:
            if self.distribute_to_extractors(deficit_extractors):
                self.distribute_to_extractor(deficit_extractors, worker)
            elif mining_bases and deficit_bases and mineral_fields_deficit:
                self.distribute_to_mineral_field(mineral_fields_deficit, worker, deficit_bases)

    def distribute_to_extractors(self, deficit_extractors):
        return self.units(EXTRACTOR).ready and deficit_extractors and not self.do_not_require_gas

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

    def force_gas_for_speedling(self):
        if (
            not self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
            and not self.collect_gas_for_speedling
        ):
            for drone in self.drones.random_group_of(3):
                self.actions.append(drone.gather(self.units(EXTRACTOR).first))
                self.collect_gas_for_speedling = True

    def distribute_gas(self):
        if not len(self.units(EXTRACTOR).ready) == 1:
            return

        self.force_gas_for_speedling()

        if self.do_not_require_gas:
            for drone in self.workers.filter(lambda drones: drones.is_carrying_vespene):
                self.actions.append(drone.gather(self.state.mineral_field.closest_to(drone)))

    @property
    def do_not_require_gas(self):
        return len(self.units(EXTRACTOR).ready) == 1 and (
            self.vespene >= 100 or self.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
        )

    def mineral_fields_of(self, bases):
        return self.state.mineral_field.filter(
            lambda field: any([field.distance_to(base) <= 8 for base in bases])
        )
