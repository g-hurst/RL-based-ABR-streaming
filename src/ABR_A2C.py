from stable_baselines3 import A2C
import sabre
from environment import ABR_Env

class ABR_A2C(sabre.Abr):
    def __init__(self, config):
        self.model = A2C.load("../models/a2c.model")

        qoe_alpha, qoe_beta, qoe_delta = (1, 1, 1)
        traces = [sabre.args.network,]
        movie = [sabre.args.movie,]
        env = ABR_Env(
            traces,
            movie,
            r_multipliers=[qoe_alpha, qoe_beta, qoe_delta],
            is_testing=True
        )
        self.env_a2c = env.get_sb_env()
        self.observation = self.env_a2c.reset()

    def get_quality_delay(self, segment_index):
        delay = 0
        quality = self.model.predict(self.observation)[0]
        print(quality)
        self.observation = self.env_a2c.step(quality)[0]

        return (quality, delay)