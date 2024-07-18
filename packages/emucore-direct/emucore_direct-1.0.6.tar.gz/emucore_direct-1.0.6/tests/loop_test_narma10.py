from time import time
import numpy as np
from emucore_direct.client import EmuCoreClient


def NARMA10(seed,train_size,test_size):
    np.random.seed(seed)
    total_size=train_size+test_size
    utrain=0.5*np.random.rand(total_size,1)
    ytrain=np.zeros((10,1))
    for i in list(range(9,total_size-1)):
        temp=0.3*ytrain[i]+0.05*ytrain[i]*np.sum(ytrain[i-10+1:i+1])+1.5*utrain[i]*utrain[i-10+1]+0.1
        ytrain=np.append(ytrain,[temp],axis=0)
    train_data={"trainInput"  :utrain[0:train_size],
                  "trainTarget" :ytrain[0:train_size]
        }
    test_data={"testInput"  :utrain[train_size:total_size],
                "testTarget" :ytrain[train_size:total_size]
                }
    dataset={
        "train_data" :   train_data,
        "test_data"     :   test_data
        }
    return dataset



if __name__ == "__main__":
    ip_addr='172.18.41.70'
    client = EmuCoreClient(ip_addr=ip_addr)
    vbias=0.31
    gain=0.72
    num_nodes=400
    num_taps=400
    input_scaling=0.1
    density=1.0
    train_size=1200
    test_size=1000
    # get lock id will release after loop
    lock_id, start, end = client.wait_for_lock()
    loop_counter = 0
    print("Entering execution loop")
    start_loop = time()
    try:
        while True:
            loop_counter+=1
            seed_iter = np.random.randint(0,10**9, size = 1)
            narma10_dataset=NARMA10(seed_iter, train_size, test_size)

            train_data=narma10_dataset["train_data"]
            test_data=narma10_dataset["test_data"]
            
            trainInput=train_data["trainInput"]
            trainTarget=train_data["trainTarget"]
            input_dim=trainInput.shape

            testInput=test_data["testInput"]
            testTarget=test_data["testTarget"]
            start_iter = time()
            reset_resp = client.reservoir_reset(lock_id=lock_id)
            config_resp = client.rc_config(lock_id=lock_id, vbias = vbias, gain=gain, num_nodes = num_nodes, num_taps=num_taps)
            train_x, trn_max_scale_val, trn_wgts = client.process_all_data(input_data=trainInput,
                         density=density,
                         num_nodes=num_nodes,
                         feature_scaling=input_scaling,
                         lock_id=lock_id,
                         seed_val_weights = seed_iter,
                         max_scale_val=None)

            test_x, test_max_scale_val,test_wgts = client.process_all_data(
                         input_data=testInput,
                         num_nodes=num_nodes,
                         density=density,
                         feature_scaling=input_scaling,
                         lock_id=lock_id,
                         seed_val_weights = seed_iter,
                         max_scale_val=trn_max_scale_val)
            end_iter = time()
            print(loop_counter, "executed loops.", "Iteration time:",  end_iter-start_iter, "seconds")
    except Exception as err:
        print("Trial loop exited with error")
        print(err)
    except KeyboardInterrupt:
        print("Trial loop interrupted by user")
    try:
        client.release_lock(lock_id=lock_id)
    except Exception:
        "Failed to release lock after execution"
    end_loop = time()
    print("Loop ran for", end_loop-start_loop, "seconds")
    print("Ending program")

        
