"""Everything related to distributing drones to the right resource goes here"""
from sc2.constants import EXTRACTOR, HATCHERY, HIVE, LAIR, ZERGLINGMOVEMENTSPEED


class DistributeWorkers:
    """Some things can be improved(mostly about the ratio mineral-vespene)"""

    def __init__(self, main):
        self.main = main
        self.mining_bases = self.mineral_fields = self.bases_deficit = self.workers_to_distribute = self.geysers = None

    async def should_handle(self):
        """Requirements to run handle"""
        self.mining_bases = self.main.units.of_type({HATCHERY, LAIR, HIVE}).ready.filter(
            lambda base: base.ideal_harvesters > 0
        )
        self.mineral_fields = self.main.state.mineral_field.filter(
            lambda field: any(field.distance_to(base) <= 8 for base in self.mining_bases)
        )
        self.bases_deficit, self.workers_to_distribute = self.calculate_distribution()
        return self.main.drones.idle or (self.workers_to_distribute and self.bases_deficit)

    async def handle(self):
        """Groups the resulting actions from all functions below"""
        self.distribute_idle_workers()
        self.gather_gas()
        self.distribute_to_deficits(self.workers_to_distribute, self.bases_deficit)
        return True

    def distribute_idle_workers(self):
        """If the worker is idle send to the closest mineral"""
        if self.mineral_fields:
            for drone in self.main.drones.idle:
                mineral_field = self.mineral_fields.closest_to(drone)
                self.main.add_action(drone.gather(mineral_field))

    def calculate_distribution(self):
        """Calculate the ideal distribution for workers"""
        workers_to_distribute = [drone for drone in self.main.drones.idle]
        self.geysers = self.main.extractors
        mineral_tags = {mf.tag for mf in self.main.state.mineral_field}
        extractor_tags = {ref.tag for ref in self.geysers}
        bases_deficit = []
        for mining_place in self.mining_bases | self.geysers.ready:
            difference = mining_place.surplus_harvesters
            if difference > 0:
                for _ in range(difference):
                    if mining_place.name == "Extractor":
                        moving_drone = self.main.drones.filter(
                            lambda x: x.order_target in extractor_tags and x not in workers_to_distribute
                        )
                    else:
                        moving_drone = self.main.drones.filter(
                            lambda x: x.order_target in mineral_tags and x not in workers_to_distribute
                        )
                    if moving_drone:
                        workers_to_distribute.append(moving_drone.closest_to(mining_place))
            elif difference < 0:
                bases_deficit.append([mining_place, difference])
        return bases_deficit, workers_to_distribute

    def mineral_fields_deficit(self, mineral_fields, bases_deficit):
        """Calculate how many workers are left to saturate the base"""
        if bases_deficit:
            return sorted(
                [mf for mf in mineral_fields.closer_than(8, bases_deficit[0][0])],
                key=lambda mineral_field: (
                    mineral_field.tag not in {worker.order_target for worker in self.main.drones.collecting},
                    mineral_field.mineral_contents,
                ),
            )
        return []

    def distribute_to_deficits(self, workers_to_distribute, bases_deficit):
        """Distribute workers so it saturates the bases"""
        bases_deficit = [x for x in bases_deficit if x[0].type_id != EXTRACTOR]
        if bases_deficit and workers_to_distribute:
            mineral_fields_deficit = self.mineral_fields_deficit(self.mineral_fields, bases_deficit)
            extractors_deficit = [x for x in bases_deficit if x[0].type_id == EXTRACTOR]
            for worker in workers_to_distribute:
                if self.mining_bases and bases_deficit and mineral_fields_deficit:
                    self.distribute_to_mineral_field(mineral_fields_deficit, worker, bases_deficit)
                if self.geysers.ready and extractors_deficit and self.require_gas:
                    self.distribute_to_extractor(extractors_deficit, worker)

    def distribute_to_extractor(self, extractors_deficit, worker):
        """Check vespene actual saturation and when the requirement are filled saturate the geyser"""
        self.main.add_action(worker.gather(extractors_deficit[0][0]))
        extractors_deficit[0][1] += 1
        if not extractors_deficit[0][1]:
            del extractors_deficit[0]

    def distribute_to_mineral_field(self, mineral_fields_deficit, worker, deficit_bases):
        """Check base actual saturation and then saturate it"""
        drone_target = mineral_fields_deficit[0]
        if len(mineral_fields_deficit) >= 2:
            del mineral_fields_deficit[0]
        self.main.add_action(worker.gather(drone_target))
        deficit_bases[0][1] += 1
        if not deficit_bases[0][1]:
            del deficit_bases[0]

    def gather_gas(self):
        """Performs the action of sending drones to geysers"""
        if self.require_gas:
            for extractor in self.geysers:
                required_drones = extractor.ideal_harvesters - extractor.assigned_harvesters
                if 0 < required_drones < self.main.drone_amount:
                    for drone in self.main.drones.random_group_of(required_drones):
                        self.main.add_action(drone.gather(extractor))

    @property
    def require_gas(self):
        """One of the requirements for gas collecting"""
        return self.require_gas_for_speedlings or self.main.vespene * 1.5 < self.main.minerals

    @property
    def require_gas_for_speedlings(self):
        """Gas collecting on the beginning so it research zergling speed fast"""
        return (
            len(self.geysers.ready) == 1
            and not self.main.already_pending_upgrade(ZERGLINGMOVEMENTSPEED)
            and self.main.vespene < 100
        )
