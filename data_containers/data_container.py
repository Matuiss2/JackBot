"""All global variables and triggers are grouped here"""
from data_containers.special_cases import SituationalData
from data_containers.our_stuff import OurStuffData
from data_containers.ungrouped_data import OtherData


class MainDataContainer(SituationalData, OurStuffData, OtherData):
    """This is the main data container for all data the bot requires"""

    def __init__(self):
        SituationalData.__init__(self)
        OurStuffData.__init__(self)
        OtherData.__init__(self)
        self.close_enemy_production = self.floated_buildings_bm = None

    def enemy_special_cases(self):
        """Pretty much makes SituationalData be updated all iterations"""
        self.prepare_enemy_data()
        self.close_enemy_production = self.check_for_proxy_buildings()
        self.floated_buildings_bm = self.check_for_floated_buildings()

    def prepare_data(self):
        """Prepares the data every iteration"""
        self.counter_attack_vs_flying = self.close_enemies_to_base = False
        self.initialize_our_stuff()
        self.initialize_enemies()
        self.prepare_bases_data()
        self.enemy_special_cases()
