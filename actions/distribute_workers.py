"""Everything related to distributing drones to the right resource goes here"""
from sc2.constants import EXTRACTOR, HATCHERY, HIVE, LAIR, ZERGLINGMOVEMENTSPEED


class DistributeWorkers:
    """Some things can be improved(mostly about the ratio mineral-vespene)"""

    def __init__(self, ai):
        self.ai = ai
        self.mining_bases = None
        self.mineral_fields = None
        self.deficit_bases = None
        self.workers_to_distribute = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        self.mining_bases = self.ai.units.of_type({HATCHERY, LAIR, HIVE}).ready.filter(
            lambda base: base.ideal_harvesters > 0
        )
        self.mineral_fields = self.mineral_fields_of(self.mining_bases)
        mining_places = self.mining_bases | self.ai.extractors.ready

        self.deficit_bases, self.workers_to_distribute = self.calculate_distribution(mining_places)

        return (self.ai.drones.idle or self.workers_to_distribute) and (self.require_gas or self.deficit_bases)

    async def handle(self, iteration):
        """Groups the resulting actions from all functions below"""
        self.gather_gas()

        self.distribute_to_deficits(
            self.mining_bases, self.workers_to_distribute, self.mineral_fields, self.deficit_bases
        )

        self.distribute_idle_workers()

        return True

    def distribute_idle_workers(self):
        """If the worker is idle send to the closest mineral"""
        for drone in self.ai.drones.idle:
            if self.mineral_fields:
                mf = self.mineral_fields.closest_to(drone)
                self.ai.add_action(drone.gather(mf))

    def calculate_distribution(self, mining_bases):
        """Calculate the ideal distribution for workers"""
        workers_to_distribute = [drone for drone in self.ai.drones.idle]
        mineral_tags = {mf.tag for mf in self.ai.state.mineral_field}
        mining_places = mining_bases | self.ai.extractors.ready
        extractor_tags = {ref.tag for ref in self.ai.extractors}
        deficit_bases = []

        for mining_place in mining_places:
            difference = mining_place.surplus_harvesters
            if difference > 0:
                for _ in range(difference):
                    if mining_place.name == "Extractor":
                        moving_drone = self.ai.drones.filter(
                            lambda x: x.order_target in extractor_tags and x not in workers_to_distribute
                        )
                    else:
                        moving_drone = self.ai.drones.filter(
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
            worker_order_targets = {worker.order_target for worker in self.ai.drones.collecting}
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
        """Distribute workers so it saturates the bases"""
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
        """Requirements to be filled to send workers to gas"""
        return self.ai.extractors.ready and deficit_extractors and self.require_gas

    def distribute_to_extractor(self, deficit_extractors, worker):
        """Check vespene actual saturation and when the requirement are filled saturate the geyser"""
        self.ai.add_action(worker.gather(deficit_extractors[0][0]))
        deficit_extractors[0][1] += 1
        if deficit_extractors[0][1] == 0:
            del deficit_extractors[0]

    def distribute_to_mineral_field(self, mineral_fields_deficit, worker, deficit_bases):
        """Check base actual saturation and then saturate it"""
        drone_target = mineral_fields_deficit[0]
        if len(mineral_fields_deficit) >= 2:
            del mineral_fields_deficit[0]
        self.ai.add_action(worker.gather(drone_target))
        deficit_bases[0][1] += 1
        if deficit_bases[0][1] == 0:
            del deficit_bases[0]

    def gather_gas(self):
        """Performs the action of sending drones to geysers"""
        if self.require_gas:
            for extractor in self.ai.extractors:
                required_drones = extractor.ideal_harvesters - extractor.assigned_harvesters
                if 0 < required_drones < self.ai.drones.amount:
                    for drone in self.ai.drones.random_group_of(required_drones):
                        self.ai.add_action(drone.gather(extractor))

    @property
    def require_gas(self):
        """One of the requirements for gas collecting"""
        return self.require_gas_for_speedlings or (self.ai.vespene < self.ai.minerals * 1.25)

    @property
    def require_gas_for_speedlings(self):
        """Gas collecting on the beginning so it research zergling speed fast"""
        return (
            len(self.ai.extractors.ready) == 1
            and not self.ai.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
            and self.ai.vespene < 100
        )

    def mineral_fields_of(self, bases):
        """See how many mineral patches are left on each base"""
        return self.ai.state.mineral_field.filter(lambda field: any([field.distance_to(base) <= 8 for base in bases]))
