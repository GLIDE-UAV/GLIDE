import os
import sys
import argparse
import numpy as np
import tensorflow as tf
sys.path.append("../")
from library.constants import *
from library.env import make_env,_test
from UAV_sim.gym_wrapper.gymEnv import UAV_sim
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.common.policies import ActorCriticPolicy
from stable_baselines.common.callbacks import BaseCallback
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
parser.add_argument('--windowless', type=str, default=windowless, help='Required windowless tag')
parser.add_argument('--draw_path', type=str, default="False", help='Required draw_path tag')

#Execution configuration
parser.add_argument('--gpu_ids', type=str, default="0", help='Required GPU IDs to run')

#Experiment details
parser.add_argument('--exp_name', type=str, default="exp", help='Required Experiment name to run')
parser.add_argument('--init_from_exp', type=str, default=None, help='Optional Experiment name to initilize weights from')

#Explore again option
parser.add_argument('--explore_again', type=str, default=explore_again, help='yes or no for explore_again after init_from_exp')

#log_loc for the ma_ppo_repo
parser.add_argument('--log_loc', type=str, default="./logs/", help='log location for the algorithm')

#Parse arguments
args = parser.parse_args()

#Setting gpu context
os.environ["CUDA_VISIBLE_DEVICES"]=args.gpu_ids


if __name__ == '__main__':
    
    envs=SubprocVecEnv([make_env(UAV_sim,rank=i,args=args) for i in range(num_of_env)])
    test_env=make_env(UAV_sim,args=args)()

    #Testing tensorboard logging
    class TensorboardCallback(BaseCallback):
        def __init__(self, verbose=0):
                self.is_tb_set = False
                self.max_reward=-np.inf
                super(TensorboardCallback, self).__init__(verbose)

        def _on_step(self):
            if self.num_timesteps%test_at_step==0:
                stat=_test(test_env=test_env,num=num_of_test,agent=self.locals['self'].model)
                if stat["avg_reward"]>self.max_reward:
                    self.max_reward=stat["avg_reward"]
                    self.locals['self'].model.save(f"./model/{args.exp_name}_ppo")
                
                summary = tf.Summary(value=[tf.Summary.Value(tag="PPO/"+tag, simple_value=val) for tag,val in stat.items()])
                self.locals['writer'].add_summary(summary, self.num_timesteps)
            return True
    
    #custom network
    class CustomPolicy(ActorCriticPolicy):
        def __init__(self, sess, ob_space, ac_space, n_env, n_steps, n_batch, reuse=False, **kwargs):
            super(CustomPolicy, self).__init__(sess, ob_space, ac_space, n_env, n_steps, n_batch, reuse=reuse, scale=True)

            with tf.variable_scope("model", reuse=reuse):
                activ = tf.nn.relu

                extracted_features = tf.layers.flatten(self.processed_obs)

                pi_h = extracted_features
                for i, layer_size in enumerate([256,256]):
                    pi_h = activ(tf.layers.dense(pi_h, layer_size, name='pi_fc' + str(i)))
                pi_latent = pi_h

                vf_h = extracted_features
                for i, layer_size in enumerate([256,256]):
                    vf_h = activ(tf.layers.dense(vf_h, layer_size, name='vf_fc' + str(i)))
                value_fn = tf.layers.dense(vf_h, 1, name='vf')
                vf_latent = vf_h

                self._proba_distribution, self._policy, self.q_value = \
                    self.pdtype.proba_distribution_from_latent(pi_latent, vf_latent, init_scale=0.01)

            self._value_fn = value_fn
            self._setup_init()

        def step(self, obs, state=None, mask=None, deterministic=False):
            if deterministic:
                action, value, neglogp = self.sess.run([self.deterministic_action, self.value_flat, self.neglogp],
                                                    {self.obs_ph: obs})
            else:
                action, value, neglogp = self.sess.run([self.action, self.value_flat, self.neglogp],
                                                    {self.obs_ph: obs})
            return action, value, self.initial_state, neglogp

        def proba_step(self, obs, state=None, mask=None):
            return self.sess.run(self.policy_proba, {self.obs_ph: obs})

        def value(self, obs, state=None, mask=None):
            return self.sess.run(self.value_flat, {self.obs_ph: obs})

    #initilize model
    model = PPO2(policy=CustomPolicy,
                env=envs,
                gamma=gamma,
                n_steps=n_steps,
                learning_rate=learning_rate,
                max_grad_norm=max_grad_norm,
                lam=lam,
                nminibatches=steps_per_epoch,
                noptepochs=epochs,
                cliprange=cliprange,
                cliprange_vf=cliprange_vf,
                tensorboard_log=args.log_loc,
                seed=args.seed)

    #Load params
    if args.init_from_exp!=None:
        model.load_parameters(f"./model/{args.init_from_exp}_ppo", explore_again=args.explore_again)

    #train
    model.learn(total_timesteps=train_for_step,
                callback=TensorboardCallback(),
                tb_log_name="PPO"+f"_{args.exp_name}_"+test_env.__repr__())