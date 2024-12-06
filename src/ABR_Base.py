import sabre
from environment import ABR_Env


class ABR_Base(sabre.Abr):
    def setup(self, model):
        self.model = model
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
        # predict quality based off the previous sabre observation
        quality = self.model.predict(self.observation)[0]
        
        # make the text observation in the next time step
        self.observation = self.env_a2c.step(quality)[0]

        # return the closest whole number to the predicted quality        
        quality = int(round(quality[0][0], 0))
        return (quality, delay)