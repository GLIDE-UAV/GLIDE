import numpy as np

def live_uav_reward(num_live,max_uav):
    return (num_live/max_uav)-1

def time_reward():
    return -1

def nothing():
    return 0

def uav_destroy():
    return -1

def mine_found():
    return +1

def target_destroy():
    return +1

class Proximity:
    def __init__(self):
        pass

    @staticmethod
    def mine_reward(min_distance,least_distance):
        return -1 * np.clip(1/min_distance,0,1/least_distance)*least_distance

    @staticmethod
    def target_reward(min_distance,least_distance):
        return (np.clip(1/min_distance,0,1/least_distance)*least_distance)-1
