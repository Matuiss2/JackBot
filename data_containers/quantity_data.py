"""All data that are related to quantity of the stuff on our possession are here"""


class OurQuantityData:
    """This is the data container for all our stuff amount"""

    def __init__(self):
        self.hydra_amount = self.zergling_amount = self.drone_amount = self.overlord_amount = self.base_amount = None
        self.ready_overlord_amount = None

    def initialize_building_amounts(self):
        self.base_amount = len(self.townhalls)

    def initialize_unit_amounts(self):
        self.hydra_amount = len(self.hydras)
        self.zergling_amount = len(self.zerglings)
        self.drone_amount = len(self.drones)
        self.overlord_amount = len(self.overlords)

    def initialize_completed_amounts(self):
        self.ready_overlord_amount = len(self.overlords.ready)
