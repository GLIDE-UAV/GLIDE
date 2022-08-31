#Environment
num_uav=4 
num_mine=3 
num_target=2 

length=60 
bredth=60 
max_height=60 
max_time=200 

uavs_at_plane=4 
detection_range=40 
distruction_range=5 
max_detection_range=60
max_uav_speed_dir=18 
max_accleration=10 
mine_radar_range=5 
target_height=6 
target_clearence=5

seed=42
same_config="False"
windowless="True"


#PPO
num_of_env=4
n_steps=512
epochs=10
steps_per_epoch=4
shuffle_buffer_size=num_of_env*n_steps
gamma=0.99
lam=0.95
vf_coef=0.5
ent_coef=0.01
learning_rate=0.00025
max_grad_norm=0.5
cliprange=0.2
cliprange_vf=None

#Training
train_for_step=10000000 #10M
test_at_step=10000
num_of_test=10
explore_again="yes"