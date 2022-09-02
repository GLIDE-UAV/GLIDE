import os
import sys
import time
import argparse
from ursina import *
sys.path.append("../")
from library.constants import *
from ursina.prefabs.memory_counter import MemoryCounter
from library.env import make_env
from UAV_sim.gym_wrapper.gymEnv import UAV_sim
from library.algo import PPO2

# Instantiate the parser
parser = argparse.ArgumentParser(description='Training for different setting with PPO')

#Environment setting
parser.add_argument('--num_uav', type=int, default=num_uav, help='Required num of uavs')
parser.add_argument('--num_mine', type=int, default=num_mine, help='Required num of mines')
parser.add_argument('--num_target', type=int, default=num_target, help='Required num of targets')

parser.add_argument('--length', type=int, default=length, help='Required length of simulation')
parser.add_argument('--bredth', type=int, default=bredth, help='Required bredth of simulation')
parser.add_argument('--max_height', type=int, default=max_height, help='Required max_height of simulation')
parser.add_argument('--max_time', type=int, default=max_time, help='Required max_time of episode')

parser.add_argument('--uavs_at_plane', type=int, default=uavs_at_plane, help='Required uavs_at_plane BS')
parser.add_argument('--detection_range', type=int, default=detection_range, help='Required detection_range of UAV')
parser.add_argument('--distruction_range', type=int, default=distruction_range, help='Required distruction_range of UAV')
parser.add_argument('--max_detection_range', type=int, default=max_detection_range, help='Required max_detection_range of UAV')
parser.add_argument('--max_uav_speed_dir', type=int, default=max_uav_speed_dir, help='Required max_uav_speed_dir of UAV')
parser.add_argument('--max_accleration', type=int, default=max_accleration, help='Required max_accleration of UAV')

parser.add_argument('--mine_radar_range', type=int, default=mine_radar_range, help='Required mine_radar_range of Mine')
parser.add_argument('--target_height', type=int, default=target_height, help='Required target_height of Target')
parser.add_argument('--target_clearence', type=int, default=target_clearence, help='Required target_clearence of Target')

parser.add_argument('--seed', type=int, default=seed, help='Required seed of the experiment')
parser.add_argument('--same_config', type=str, default=same_config, help='Required same_config tag')
parser.add_argument('--windowless', type=str, default="False", help='Required windowless tag')
parser.add_argument('--draw_path', type=str, default="True", help='Required draw_path tag')

#Execution configuration
parser.add_argument('--gpu_ids', type=str, default="0", help='Required GPU IDs to run')

#Experiment details
parser.add_argument('--init_from_exp', type=str, default="exp", help='Optional Experiment name to initilize weights from')

#Random actions
parser.add_argument('--random', type=str, default="no",help='Optional Random action')

#Add delay
parser.add_argument('--delay', type=float, default=0,help='Optional delay added between each rendered frames')

#Parse arguments
args = parser.parse_args()

#Setting gpu context
os.environ["CUDA_VISIBLE_DEVICES"]=args.gpu_ids

test_env=make_env(UAV_sim,args=args)()
if args.init_from_exp!=None and args.random=="no":
    model=PPO2.load(f"./model/{args.init_from_exp}_ppo")
    randomFlag=False
elif args.random=="yes":
    randomFlag=True
else:
    raise Exception("init_from_exp tag must be passes to test performance")

episode_reward=0
delay=args.delay
curr_state=test_env.reset()
skip=False

if args.windowless=="True":
    def update():
        global episode_reward,curr_state
        if randomFlag==False:
            action, _states = model.predict(curr_state)
        else:
            action=test_env.action_space.sample()

        next_state, reward, done, info = test_env.step(action)
        episode_reward+=reward
        curr_state=next_state
            
        if done:
            print("episode reward: {}\nend for : {}".format(episode_reward,info))
            print("Remaining objects are: ",len(scene.entities))
            episode_reward=0
            curr_state=test_env.reset()
else:
    def update():
        global episode_reward,curr_state,skip
        if not skip:
            time.sleep(delay)
            if randomFlag==False:
                action, _states = model.predict(curr_state)
            else:
                action=test_env.action_space.sample()

            next_state, reward, done, info = test_env.step(action)
            episode_reward+=reward
            curr_state=next_state
                
            if done:
                print("episode reward: {}\nend for : {}".format(episode_reward,info))
                print("Remaining objects are: ",len(scene.entities))
                skip=True
            

    def input(event):
        global episode_reward,curr_state,skip
        if event=='u':
            episode_reward=0
            curr_state=test_env.reset()
            skip=False

    camera.set_position(Vec3(0, 0, -588.445))
    EditorCamera()
    MemoryCounter()
    pannel=\
    f"""
        UAV={args.num_uav}
        Mine={args.num_mine}
        Target={args.num_target}

        Length={args.length}
        Bredth={args.bredth}
        Height={args.max_height}
        Max time={args.max_time}

        Restart tap 'u'
    """
    Text(pannel,position=window.top_left)

test_env.env.app.run()