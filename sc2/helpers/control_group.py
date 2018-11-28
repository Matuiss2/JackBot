"""Group helpers for creating control groups"""


class ControlGroup(set):
    """Helpers for creating control groups"""

    def __init__(self, units):
        super().__init__({unit.tag for unit in units})

    def __hash__(self):
        return hash(tuple(sorted(list(self))))

    def select_units(self, units):
        """Select all units with the same tag"""
        return units.filter(lambda unit: unit.tag in self)

    def missing_unit_tags(self, units):
        """Group all units of the type that are not on the control group"""
        return {t for t in self if units.find_by_tag(t) is None}

    def add_unit(self, unit):
        """Add unit to the control group"""
        self.add(unit.tag)

    def add_units(self, units):
        """Add a group of units if the same type to the control group"""
        for unit in units:
            self.add_unit(unit)

    def remove_unit(self, unit):
        """Remove unit from the control group"""
        self.remove(unit.tag)

    def remove_units(self, units):
        """Remove a group of units if the same type from the control group"""
        for unit in units:
            self.remove(unit.tag)
