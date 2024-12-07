import gymnasium as gym
import numpy as np
from stable_baselines3.common.vec_env import DummyVecEnv
from emulator import Emulator
import sabre

class ABR_Env(gym.Env):
    def __init__(self, network_traces, movies, r_multipliers=[1, 1, 1], is_testing=False):
        self.is_testing     = is_testing
        self.r_multipliers  = r_multipliers
        self.network_traces = network_traces
        self.trace_idx      = 0
        self.movies         = movies
        self.movie_idx      = 1
        self.emulator   = Emulator(movies[0], network_traces[0])
        self.look_ahead = 5
        self.look_back  = 5
        self.n_bitrates = len(self.emulator.bitrates)

        self.observation_space = gym.spaces.Dict({
            'qualities':       gym.spaces.Box(low=0, 
                                              high=np.inf, 
                                              shape=(self.look_ahead, self.n_bitrates), 
                                              dtype=np.float32),
            'buffer_level':    gym.spaces.Box(low=0, high=np.inf, dtype=np.float32), 
            'throughput':      gym.spaces.Box(low=0, high=np.inf, shape=(3,), dtype=np.float32),
            'latency':         gym.spaces.Box(low=0, high=np.inf, shape=(3,), dtype=np.float32),
        })
        self.throughput_prev = []
        self.latency_prev = []
        
        self.action_space = gym.spaces.Box(low=0, high=self.n_bitrates-1, dtype=np.float32)
        self.action_prev = None

    def step(self, action):
        truncated = False
        info = {}

        # action is a bitrate index, so round to the nearest whole number
        action = int(round(action[0], 0))

        if self.is_testing:
            # get latency, throutput, and rebuff_time from sabre globals
            throughput = sabre.t
            latency    = sabre.l
            rebuff_time = sabre.rebuffer_time - self.emulator.last_rebuff_time
            self.emulator.last_rebuff_time = sabre.rebuffer_time
        else:
            # take the action in the emulator and update accordingly
            throughput, latency, rebuff_time = self.emulator.step(action)
            
        self.throughput_prev.append(throughput)
        if len(self.throughput_prev) > self.look_back:
            self.throughput_prev.pop(0)
        self.latency_prev.append(latency)
        if len(self.latency_prev) > self.look_back:
            self.latency_prev.pop(0)
        
        observation = self.get_observation(throughput, latency)
        # print(observation)
        # check if the quality changed from the last bitrate selection action
        q_change = 0
        if self.action_prev is not None:
            q_change = abs(self.action_prev - action)
        self.action_prev = action
        
        # calculate the qoe at the current time step
        reward = (action * self.r_multipliers[0]) - (q_change * self.r_multipliers[1]) - (rebuff_time * self.r_multipliers[2])

        # once the movie has ended, a terminal state is reached
        is_terminal = (self.emulator.get_n_segs_left() == 0)
        # print(f'getting reward {reward} = {action * self.r_multipliers[0]} - {q_change * self.r_multipliers[1]} - {rebuff_time * self.r_multipliers[2]}')
        return observation, reward, is_terminal, truncated, info

    def reset(self, seed=None):
        info = {}
        if self.trace_idx == 0:
            # move on to the next movie now that the trace is over
            self.movie_idx = (self.movie_idx + 1) % len(self.movies)
        else:
            # move on to the to the next trace with the same movie
            self.trace_idx = (self.trace_idx + 1) % len(self.network_traces)

        # create a new instance of the emulator now that the trace/movie has been incramented
        # this is important because it resets a LOT of sabre global variables
        self.emulator  = Emulator(self.movies[self.movie_idx], self.network_traces[self.trace_idx])
        observation = self.get_observation(0, 0)

        return observation, info

    def get_observation(self, throughput, latency):
        observation = {}
        seg = self.emulator.current_segment
        segs_left   =  self.emulator.get_n_segs_left()
        observation['buffer_level'] = self.emulator.get_buffer_level()
        
        # the look_ahead segment sizes are set to zero when nearing the end of
        # the movie and there are no more to look at. 
        if segs_left >= self.look_ahead:
            observation['qualities'] = self.emulator.get_segs(seg, seg+self.look_ahead)
        elif segs_left > 0:
            observation['qualities'] = np.array(self.emulator.get_segs(seg, seg+segs_left), dtype=np.float32)
            zeros = np.zeros((self.look_ahead - segs_left, self.n_bitrates), dtype=np.float32)
            observation['qualities'] = np.vstack((observation['qualities'],zeros))
        else:
            observation['qualities'] = np.zeros((self.look_ahead, self.n_bitrates), dtype=np.float32)

        # througput values are initally set to zero when no observations have been made yet
        throughput_obs = np.zeros(3)
        throughput_obs[0] = throughput
        if len(self.throughput_prev) > 0:
            throughput_obs[1] = np.mean(self.throughput_prev)
            throughput_obs[2] = np.std(self.throughput_prev)
        observation['throughput'] = throughput_obs

        latency_obs = np.zeros(3)
        latency_obs[0] = latency
        if len(self.latency_prev) > 0:
            latency_obs[1] = np.mean(self.latency_prev)
            latency_obs[2] = np.std(self.latency_prev)
        observation['latency'] = latency_obs

        # sanity check that all observation keys have values
        assert all(o is not None for o in observation.values())

        return observation

    def get_sb_env(self):
        return DummyVecEnv([lambda: self])
