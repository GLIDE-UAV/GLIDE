import pickle
import argparse
from library.helper import evaluate
from multiprocessing import Process,Lock,Manager

parser = argparse.ArgumentParser(description='Getting results')
parser.add_argument('--num_test', type=int, default=10, help='Required num of tests to run') #should give --num_test=100
args = parser.parse_args()

fix=lambda i,exp,exp_id: i if exp==exp_id else 4
modes=['dis','cent']
uav_exp=dict([("default_exp",eval("dict(num_uav=4,num_mine=4,num_target=4)"))]+\
            [(f"{exp}{i}",eval(f"dict(num_uav={fix(i,exp,'uav')},num_mine={fix(i,exp,'mine')},num_target={fix(i,exp,'target')})"))\
            for exp in ["uav","mine","target"] for i in [1,2,3,5,6]])

def eval_fn(uav_exp,mode,exp_name,num_test,d,l):
    res=evaluate(uav_exp,mode,exp_name,num_test)
    l.acquire()
    try:
        d[exp_name+"_"+mode]=res
    finally:
        l.release()

def get_Results(uav_exp,num_test=10):
    res=None
    lock=Lock()
    with Manager() as manager:
        d = manager.dict()
        threads=[Process(target=eval_fn,args=(uav_exp,mode,exp_name,num_test,d,lock)) \
                for mode in modes \
                for exp_name in uav_exp.keys()]
        for p in threads:
            p.start()
            p.join()
        res=dict(d.items())
    return res

res=get_Results(uav_exp,num_test=args.num_test)
with open('./logs/dump/res.pkl', 'wb') as handle:
    pickle.dump(res, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('./logs/dump/res.pkl', 'rb') as handle:
#     res = pickle.load(handle)

#NICE