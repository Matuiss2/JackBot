"""All data that are related to quantity of the stuff on our possession are here"""
from sc2.constants import UnitTypeId


class OurQuantityData:
    """This is the data container for all our stuff amounts"""

    def __init__(self):
        self.hydra_amount = self.zergling_amount = self.overlord_amount = self.ovs_in_queue = self.drone_amount = None
        self.ready_overlord_amount = self.ready_base_amount = self.hatcheries_in_queue = self.base_amount = None
        self.drones_in_queue = self.ultra_amount = None

    def buildings_amounts(self):
        """Defines the amount of buildings on our possession separating by type"""
        self.base_amount = len(self.townhalls)

    def completed_asset_amounts(self):
        """Defines the amount of units and buildings that are finished on our possession separating by type"""
        self.ready_overlord_amount = len(self.overlords.ready)
        self.ready_base_amount = len(self.ready_bases)

    def incomplete_asset_amounts(self):
        """Defines the amount of units and buildings that are in progress on our possession separating by type"""
        self.hatcheries_in_queue = self.already_pending(UnitTypeId.HATCHERY)
        self.ovs_in_queue = self.already_pending(UnitTypeId.OVERLORD)
        self.drones_in_queue = self.already_pending(UnitTypeId.DRONE)

    def unit_amounts(self):
        """Defines the amount of units on our possession separating by type"""
        self.hydra_amount = len(self.hydras)
        self.ultra_amount = len(self.ultralisks)
        self.zergling_amount = len(self.zerglings)
        self.drone_amount = self.supply_workers
        self.overlord_amount = len(self.overlords)
