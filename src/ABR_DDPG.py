from stable_baselines3 import DDPG
from ABR_Base import ABR_Base

class ABR_DDPG(ABR_Base):
    def __init__(self, config):
        model = DDPG.load("../models/ddpg.model")
        self.setup(model)