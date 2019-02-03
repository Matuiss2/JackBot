"""Everything related to distributing drones to the right resource goes here"""
from sc2.constants import EXTRACTOR, HATCHERY, HIVE, LAIR, ZERGLINGMOVEMENTSPEED


class DistributeWorkers:
    """Some things can be improved(mostly about the ratio mineral-vespene)"""

    def __init__(self, main):
        self.controller = main
        self.mining_bases = self.mineral_fields = self.deficit_bases = self.workers_to_distribute = None

    async def should_handle(self):
        """Requirements to run handle"""
        self.mining_bases = self.controller.units.of_type({HATCHERY, LAIR, HIVE}).ready.filter(
            lambda base: base.ideal_harvesters > 0
        )
        self.mineral_fields = self.controller.state.mineral_field.filter(
            lambda field: any(field.distance_to(base) <= 8 for base in self.mining_bases)
        )
        mining_places = self.mining_bases | self.controller.extractors.ready
        self.deficit_bases, self.workers_to_distribute = self.calculate_distribution(mining_places)
        return self.controller.drones.idle or (self.workers_to_distribute and self.deficit_bases)

    async def handle(self):
        """Groups the resulting actions from all functions below"""
        self.distribute_idle_workers()
        self.gather_gas()
        self.distribute_to_deficits(self.workers_to_distribute, self.deficit_bases)
        return True

    def distribute_idle_workers(self):
        """If the worker is idle send to the closest mineral"""
        if self.mineral_fields:
            for drone in self.controller.drones.idle:
                mineral_field = self.mineral_fields.closest_to(drone)
                self.controller.add_action(drone.gather(mineral_field))

    def calculate_distribution(self, mining_bases):
        """Calculate the ideal distribution for workers"""
        workers_to_distribute = [drone for drone in self.controller.drones.idle]
        mineral_tags = {mf.tag for mf in self.controller.state.mineral_field}
        mining_places = mining_bases | self.controller.extractors.ready
        extractor_tags = {ref.tag for ref in self.controller.extractors}
        deficit_bases = []
        for mining_place in mining_places:
            difference = mining_place.surplus_harvesters
            if difference > 0:
                for _ in range(difference):
                    if mining_place.name == "Extractor":
                        moving_drone = self.controller.drones.filter(
                            lambda x: x.order_target in extractor_tags and x not in workers_to_distribute
                        )
                    else:
                        moving_drone = self.controller.drones.filter(
                            lambda x: x.order_target in mineral_tags and x not in workers_to_distribute
                        )
                    if moving_drone:
                        workers_to_distribute.append(moving_drone.closest_to(mining_place))
            elif difference < 0:
                deficit_bases.append([mining_place, difference])
        return deficit_bases, workers_to_distribute

    def mineral_fields_deficit(self, mineral_fields, deficit_bases):
        """Calculate how many workers are left to saturate the base"""
        if deficit_bases:
            worker_order_targets = {worker.order_target for worker in self.controller.drones.collecting}
            mineral_fields_deficit = [mf for mf in mineral_fields.closer_than(8, deficit_bases[0][0])]
            return sorted(
                mineral_fields_deficit,
                key=lambda mineral_field: (
                    mineral_field.tag not in worker_order_targets,
                    mineral_field.mineral_contents,
                ),
            )
        return []

    def distribute_to_deficits(self, workers_to_distribute, deficit_bases):
        """Distribute workers so it saturates the bases"""
        deficit_bases = [x for x in deficit_bases if x[0].type_id != EXTRACTOR]
        if deficit_bases and workers_to_distribute:
            mineral_fields_deficit = self.mineral_fields_deficit(self.mineral_fields, deficit_bases)
            deficit_extractors = [x for x in deficit_bases if x[0].type_id == EXTRACTOR]
            for worker in workers_to_distribute:
                if self.mining_bases and deficit_bases and mineral_fields_deficit:
                    self.distribute_to_mineral_field(mineral_fields_deficit, worker, deficit_bases)
                if self.controller.extractors.ready and deficit_extractors and self.require_gas:
                    self.distribute_to_extractor(deficit_extractors, worker)

    def distribute_to_extractor(self, deficit_extractors, worker):
        """Check vespene actual saturation and when the requirement are filled saturate the geyser"""
        self.controller.add_action(worker.gather(deficit_extractors[0][0]))
        deficit_extractors[0][1] += 1
        if not deficit_extractors[0][1]:
            del deficit_extractors[0]

    def distribute_to_mineral_field(self, mineral_fields_deficit, worker, deficit_bases):
        """Check base actual saturation and then saturate it"""
        drone_target = mineral_fields_deficit[0]
        if len(mineral_fields_deficit) >= 2:
            del mineral_fields_deficit[0]
        self.controller.add_action(worker.gather(drone_target))
        deficit_bases[0][1] += 1
        if not deficit_bases[0][1]:
            del deficit_bases[0]

    def gather_gas(self):
        """Performs the action of sending drones to geysers"""
        if self.require_gas:
            for extractor in self.controller.extractors:
                required_drones = extractor.ideal_harvesters - extractor.assigned_harvesters
                if 0 < required_drones < len(self.controller.drones):
                    for drone in self.controller.drones.random_group_of(required_drones):
                        self.controller.add_action(drone.gather(extractor))

    @property
    def require_gas(self):
        """One of the requirements for gas collecting"""
        return self.require_gas_for_speedlings or self.controller.vespene * 1.5 < self.controller.minerals

    @property
    def require_gas_for_speedlings(self):
        """Gas collecting on the beginning so it research zergling speed fast"""
        return (
            len(self.controller.extractors.ready) == 1
            and not self.controller.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
            and self.controller.vespene < 100
        )
