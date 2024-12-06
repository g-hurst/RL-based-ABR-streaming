from stable_baselines3 import A2C
from ABR_Base import ABR_Base

class ABR_A2C(ABR_Base):
    def __init__(self, config):
        model = A2C.load("../models/a2c.model")
        self.setup(model)