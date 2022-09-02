<!-- Multi-Agent Proximal Policy Optimization -->
<!-- use # https://github.com/Stable-Baselines-Team/stable-baselines-tf2.git -->

# D-GLIDE
The decentralized action control of GLIDE. The Multi-Agent Proximal Policy Optimization in GLIDE uses [stable-baselines](https://github.com/Stable-Baselines-Team/stable-baselines-tf2.git)
## Steps to run GLIDE

After setting up the UAV_sim environment, you can run the D-GLIDE algorithm.

You can run D-GLIDE test and train files using the following commands with the default settings.

```
python3 train.py 

python3 test.py 
```

If you wish to customize settings, you can use the following commands.

`````
python3 train.py --exp_name="default_exp" --num_uav=<number of UAVs> --num_mine=<number of mines> --num_target=<number of targets> --gpu_ids="0"

python3 test.py --init_from_exp="default_exp" --num_uav=<number of UAVs> --num_mine=<number of mines> --num_target=<number of targets> --windowless="True"
`````


<!-- ## License -->
[MIT LICENSE](LICENSE)
