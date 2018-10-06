"""The base for actions to inherit from"""

class Action:
    """The base for an action"""

    def __init__(self, ai):
        self.ai = ai

    def should_handle(self, iteration: int):
        """Should this action be handled"""
        return iteration > 0
