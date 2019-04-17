"""Everything related to distributing drones to the right resource goes here"""
from itertools import repeat
from sc2.constants import UnitTypeId, UpgradeId


class DistributeWorkers:
    """Some things can be improved(mostly about the ratio mineral-vespene)"""

    def __init__(self, main):
        self.main = main
        self.mining_bases = self.mineral_fields = self.bases_deficit = self.workers_to_distribute = None
        self.geyser_tags = None

    async def should_handle(self):
        """Requirements to run handle"""
        self.mining_bases = self.main.ready_bases.filter(lambda base: base.ideal_harvesters > 0)
        self.mineral_fields = self.main.state.mineral_field.filter(
            lambda field: any(field.distance_to(base) <= 8 for base in self.mining_bases)
        )
        self.bases_deficit, self.workers_to_distribute = self.calculate_distribution()
        return self.workers_to_distribute or self.bases_deficit

    async def handle(self):
        """Groups the resulting actions from all functions below"""
        self.distribute_idle_workers()
        self.gather_gas()
        self.transfer_to_minerals()
        self.distribute_to_deficits()

    def calculate_distribution(self):
        """Calculate the ideal distribution for workers"""
        workers_to_distribute = self.main.drones.idle
        mineral_tags = {mf.tag for mf in self.main.state.mineral_field}
        self.geyser_tags = {ref.tag for ref in self.main.extractors}
        bases_deficit = []
        for mining_place in self.mining_bases | self.main.extractors.ready:
            difference = mining_place.surplus_harvesters
            if difference > 0:
                for _ in repeat(None, difference):
                    if mining_place.name == "Extractor":
                        moving_drones = self.main.drones.filter(
                            lambda x: x.order_target in self.geyser_tags and x not in workers_to_distribute
                        )
                    else:
                        moving_drones = self.main.drones.filter(
                            lambda x: x.order_target in mineral_tags and x not in workers_to_distribute
                        )
                    workers_to_distribute.append(moving_drones.closest_to(mining_place))
            elif difference < 0:
                bases_deficit.append([mining_place, difference])
        return bases_deficit, workers_to_distribute

    def distribute_idle_workers(self):
        """If the worker is idle send to the closest mineral"""
        if self.mineral_fields:
            for drone in self.main.drones.idle:
                self.main.add_action(drone.gather(self.mineral_fields.closest_to(drone)))

    def distribute_to_deficits(self):
        """Distribute workers so it saturates the bases"""
        bases_deficit = [x for x in self.bases_deficit if x[0].type_id != UnitTypeId.EXTRACTOR]
        if bases_deficit and self.workers_to_distribute:
            mineral_fields_deficit = self.mineral_fields_deficit(bases_deficit)
            extractors_deficit = [x for x in bases_deficit if x[0].type_id == UnitTypeId.EXTRACTOR]
            for worker in self.workers_to_distribute:
                self.distribute_to_mineral_field(mineral_fields_deficit, worker, bases_deficit)
                self.distribute_to_extractor(extractors_deficit, worker)

    def distribute_to_extractor(self, extractors_deficit, worker):
        """Check vespene actual saturation and when the requirement are filled saturate the geyser"""
        if self.main.extractors.ready and extractors_deficit and self.require_gas:
            self.main.add_action(worker.gather(extractors_deficit[0][0]))
            extractors_deficit[0][1] += 1
            if not extractors_deficit[0][1]:
                del extractors_deficit[0]

    def distribute_to_mineral_field(self, mineral_fields_deficit, worker, bases_deficit):
        """Check base actual saturation and then saturate it"""
        if bases_deficit and mineral_fields_deficit:
            if len(mineral_fields_deficit) >= 2:
                del mineral_fields_deficit[0]
            self.main.add_action(worker.gather(mineral_fields_deficit[0]))
            bases_deficit[0][1] += 1
            if not bases_deficit[0][1]:
                del bases_deficit[0]

    def gather_gas(self):
        """Performs the action of sending drones to geysers"""
        if self.require_gas:
            drones_gathering_amount = len(self.main.drones.gathering)
            for extractor in self.main.extractors:
                required_drones = extractor.ideal_harvesters - extractor.assigned_harvesters
                if 0 < required_drones < drones_gathering_amount:
                    for drone in self.main.drones.gathering.sorted_by_distance_to(extractor).take(required_drones):
                        self.main.add_action(drone.gather(extractor))

    def mineral_fields_deficit(self, bases_deficit):
        """Calculate how many workers are left to saturate the base"""
        return sorted(
            [mf for mf in self.mineral_fields.closer_than(8, bases_deficit[0][0])],
            key=lambda mineral_field: (
                mineral_field.tag not in {worker.order_target for worker in self.main.drones.collecting},
                mineral_field.mineral_contents,
            ),
        )

    @property
    def require_gas(self):
        """One of the requirements for gas collecting"""
        return (
            self.require_gas_for_speedlings
            or self.main.vespene * 1.5 < self.main.minerals
            and self.main.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) in (0, 1)
        )

    @property
    def require_gas_for_speedlings(self):
        """Gas collecting on the beginning so it research zergling speed fast"""
        return (
            len(self.main.extractors.ready) == 1
            and not self.main.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED)
            and self.main.vespene < 100
        )

    def transfer_to_minerals(self):
        """ Transfer drones from vespene to minerals when vespene count is way to high
         or early when zergling speed is being upgraded"""
        if (
            self.main.vespene > self.main.minerals * 4
            and self.main.minerals >= 75
            or self.main.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) not in (0, 1)
        ):
            if self.mineral_fields:
                for drone in self.main.drones.gathering.filter(lambda x: x.order_target in self.geyser_tags):
                    self.main.add_action(drone.gather(self.mineral_fields.closest_to(drone)))
