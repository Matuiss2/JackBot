from sc2.constants import HATCHERY, PROBE, DRONE, SCV, EXTRACTOR, LAIR, HIVE, LARVA, OVERLORD, SPAWNINGPOOL, ZERGLING


class worker_control:
    def __init__(self):
        self.defense_mode = False
        self.defenders = None
        self.defender_tags = None

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

    async def split_workers(self):
        for drone in self.units(DRONE):
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        lowesthp = min(enemy.health for enemy in enemies)
        low_enemies = enemies.filter(lambda x: x.health == lowesthp)
        target = low_enemies.closest_to(unit)
        self.actions.append(unit.attack(target))

    async def defend_worker_rush(self):
        """Its the way I found to defend simple worker rushes,
            I don't know if it beats complexes worker rushes like tyr's bot"""
        base = self.units(HATCHERY)
        if base:
            enemy_units_close = self.known_enemy_units.closer_than(8, base.first).of_type([PROBE, DRONE, SCV])
            if enemy_units_close and not self.defense_mode:
                self.defense_mode = True
                self.defender_tags = [
                    unit.tag for unit in self.units(DRONE).random_group_of(2 * (len(enemy_units_close)))
                ]
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
                self.defenders = self.units(DRONE).filter(
                    lambda worker: worker.tag in self.defender_tags and worker.health > 0
                )
                defender_deficit = min(len(self.units(DRONE)) - 1, 2 * len(enemy_units_close)) - len(self.defenders)
                if defender_deficit > 0:
                    additional_drones = [
                        unit.tag
                        for unit in self.units(DRONE)
                        .filter(lambda worker: worker.tag not in self.defender_tags)
                        .random_group_of(defender_deficit)
                    ]
                    self.defender_tags = self.defender_tags + additional_drones
                for drone in self.defenders:
                    # 6 hp is the lowest you can take a hit and still survive
                    if drone.health <= 6:
                        if not drone.is_collecting:
                            mineral_field = self.state.mineral_field.closest_to(base.first.position)
                            self.actions.append(drone.gather(mineral_field))
                            continue
                        else:
                            pass
                    else:
                        if drone.weapon_cooldown == 0:
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
                            lowest_hp_enemy = min(enemy_units_close, key=(lambda x: x.health + x.shield))
                            self.actions.append(drone.move(lowest_hp_enemy))
                            continue

    async def distribute_workers(self):
        workers_to_distribute = [drone for drone in self.units(DRONE).idle]
        deficit_bases = []
        deficit_extractors = []
        mineral_fields_deficit = []
        extractor_tags = {ref.tag for ref in self.units(EXTRACTOR)}
        mineral_tags = {mf.tag for mf in self.state.mineral_field}
        mining_bases = self.units.of_type({HATCHERY, LAIR, HIVE}).ready.filter(lambda base: base.ideal_harvesters > 0)
        mineral_fields = self.state.mineral_field.filter(
            lambda field: any([field.distance_to(base) <= 8 for base in mining_bases])
        )
        # check places to collect from whether there are not optimal worker counts
        for mining_place in mining_bases | self.units(EXTRACTOR).ready:
            difference = mining_place.surplus_harvesters
            # if too many workers, put extra workers in workers_to_distribute
            if difference > 0:
                for _ in range(difference):
                    if mining_place.name == "Extractor":
                        moving_drone = self.units(DRONE).filter(
                            lambda x: x.order_target in extractor_tags and x not in workers_to_distribute
                        )
                    else:
                        moving_drone = self.units(DRONE).filter(
                            lambda x: x.order_target in mineral_tags and x not in workers_to_distribute
                        )
                    if moving_drone:
                        workers_to_distribute.append(moving_drone.closest_to(mining_place))
            # too few workers, put place to mine in deficit list
            elif difference < 0:
                if mining_place.name == "Extractor":
                    deficit_extractors.append([mining_place, difference])
                else:
                    deficit_bases.append([mining_place, difference])

        if len(deficit_bases) + len(deficit_extractors) == 0:
            # no deficits so only move idle workers, not surplus and idle
            for drone in self.units(DRONE).idle:
                if mineral_fields:
                    mf = mineral_fields.closest_to(drone)
                    self.actions.append(drone.gather(mf))
            return
        worker_order_targets = {worker.order_target for worker in self.units(DRONE).collecting}
        # order mineral fields for scvs to prefer the ones with no worker and most minerals
        if deficit_bases and workers_to_distribute:
            mineral_fields_deficit = [mf for mf in mineral_fields.closer_than(8, deficit_bases[0][0])]
            # order target mineral fields, first by if someone is there already, second by mineral content
            mineral_fields_deficit = sorted(
                mineral_fields_deficit,
                key=lambda mineral_field: (
                    mineral_field.tag not in worker_order_targets,
                    mineral_field.mineral_contents,
                ),
            )
        for worker in workers_to_distribute:
            # distribute to refineries
            if self.units(EXTRACTOR).ready and deficit_extractors:
                self.actions.append(worker.gather(deficit_extractors[0][0]))
                deficit_extractors[0][1] += 1
                if deficit_extractors[0][1] == 0:
                    del deficit_extractors[0]
            # distribute to mineral fields
            elif mining_bases and deficit_bases and mineral_fields_deficit:
                drone_target = mineral_fields_deficit[0]
                if len(mineral_fields_deficit) >= 2:
                    del mineral_fields_deficit[0]
                self.actions.append(worker.gather(drone_target))
                deficit_bases[0][1] += 1
                if deficit_bases[0][1] == 0:
                    del deficit_bases[0]
            else:
                pass
