#Environment
num_uav=4#1 
num_mine=4#3 
num_target=8#3 

length=100 
bredth=100 
max_height=50 
max_time=300 

uavs_at_plane=4 
detection_range=30 
distruction_range=10 
max_detection_range=60
max_uav_speed_dir=1.8*5 
max_accleration=1.0*5
mine_radar_range=5 
target_height=4 
target_clearence=1

seed=42
same_config="False"
windowless="True"


#PPO
num_of_env=6
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
train_for_step=50000000 #50M
test_at_step=20000
num_of_test=10
explore_again="yes"