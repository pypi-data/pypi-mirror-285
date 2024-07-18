import struct
import numpy as np
from scipy import signal
from scipy.sparse import random
from scipy.stats import uniform

MAX_PACKET_SIZE=20*1024*1024
DIGITIZE_FACTOR = pow(2,28)
MAX_FILTER_COEFS=520
SAMPLE_RATE = 1E6
# filter settings
BAND_PASS = [6E3, 494E3]
TRANS_WIDTH = 5E3
EDGES = [0,
         BAND_PASS[0] - TRANS_WIDTH,
         BAND_PASS[0], 
         BAND_PASS[1],
         BAND_PASS[1] + TRANS_WIDTH, 
         0.5*SAMPLE_RATE]


def set_filter_coefficients(num_taps: int) -> np.ndarray:
    """
    Set filter coefficients

    :param num_taps: number of connections in reservoir, generally should be less
           than the number of nodes in reservoir.

    :return: a 1 dimensional array of the filter coefficients.
    """
    # max coef size 520
    num_coefs = min(MAX_FILTER_COEFS, num_taps)
    filt_coefs = signal.remez(num_coefs, EDGES, [0, 1, 0], fs=SAMPLE_RATE)

    filt_coefs=filt_coefs*(1/(np.max(filt_coefs))) /2 #should be between +/-0.5
    filt_coefs=filt_coefs*(2**32-1)/(2**32)        
    if(num_coefs<MAX_FILTER_COEFS):
        zeros_arr=np.zeros(shape=(int(MAX_FILTER_COEFS-num_coefs)))
        filt_coefs=np.concatenate([filt_coefs,zeros_arr])
    filt_coefs=filt_coefs.reshape(-1,10)
    filt_coefs=np.flipud(filt_coefs)
    filt_coefs=filt_coefs.flatten()
    filt_coefs = (filt_coefs*2**31).astype("int32")
    return filt_coefs


def set_weights(num_features: int,
                num_nodes: int,
                density: float=0.1,
                seed_val: int=13)->np.ndarray:
    """
    Randomly sets weights between -1 and 1 with specific level of sparsity

    :param num_features: number of fetaures in the data set
    :param num_nodes: the number of resevoir nodes for run
    :param density: percent of entries in weights to be non-zero
    :param seed_val: seeds randomness for weigths to allow for reproducibility 
    :return: num_features x num_nodes matrix of weights
    """
    assert density<=1 and density>=0, "Must specify density for  weights in range [0,1]"
    np.random.seed(seed_val)
    unif_rv = uniform(loc=-1, scale=2).rvs
    weights = random(m=num_features, 
                     n=num_nodes , 
                     density=density, 
                     random_state=13, 
                     data_rvs=unif_rv)
    return weights.toarray()

def create_data_packets(flattened_data: list):
    """
    Creates packets of appropriate size to send sequentially to the reservoir computer
    
    :param flattened data: a list of lists where each sublist is a packet that is
       of appropriate size for the reservoir.
    """
    packet_lists = []
    for i in range(0, len(flattened_data), MAX_PACKET_SIZE):
        sublist = flattened_data[i:i+MAX_PACKET_SIZE]
        packet_lists.append(sublist)
    return packet_lists

def prep_input_data(input_data: np.ndarray,
                    num_nodes: int,
                    density: float,
                    feature_scaling: float,
                    max_scale_val: float=None,
                    weights: np.ndarray=None,
                    seed_val_weights: int=13)->np.ndarray:
    """
    Prep input data for reservoir by:
    
    1. Set and apply weights
    2. Apply scaling
    3. Digitize data
    4. Split into packets

    :param input_data: a numpy array to be scaled
    :param num_nodes: the number of nodes which will be applied in the reservoir.
    :param feature_scaling: after applying max abs scalar feature scaling factor applied
    :param max_scale_val: the max scaling value to apply to input data
    :param seed_val_weights: seeds randomness for weigths to allow for reproducibility
    :returns:
      a tuple with the following elements:

      - prepped_data: rescaled and split input data into packets
      - max_scale: the max abs value in dataset with which scaling was applied
      - weights: array of weights that were applied as a mask to the data.\

    :note: could use other scaling methods
    """
    num_rows, num_features = input_data.shape
    if weights is None:
        weights = set_weights(num_features=num_features,
                              num_nodes=num_nodes,
                              density=density,
                              seed_val=seed_val_weights)
    else:
        wgt_m, wgt_n = weights.shape
        assert wgt_m==num_features and wgt_n==num_nodes, \
            f"`weights` input dimension ({wgt_m}, {wgt_n}) must match dimension (num_features, num_nodes)=({num_features}, {num_nodes})"
    # apply weights
    input_data = np.dot(input_data, weights)
    # apply scaling
    if not max_scale_val:
        max_scale_val = np.max(np.abs(input_data))
    input_data = DIGITIZE_FACTOR*feature_scaling*input_data/max_scale_val
    input_data = input_data.astype(np.int32)
    input_data = input_data.flatten(order="C")
    return create_data_packets(flattened_data = input_data.tolist()), max_scale_val, weights

def bytes_to_array(input_bytes: bytes):
    """
    Converts a bytes  to an array of integers

    :param input_bytes: bytes from the reservoir states
    :return: array of integers representing the reservoir states
    """
    input_length = len(input_bytes)
    pack_format = "i"
    data_list=struct.unpack(f"{input_length//4}{pack_format}",input_bytes)
    return np.array(data_list)*2**(-31)

def message_to_dict(grpc_message):
    """
    Converts a grpc message to a dictionary

    :param grpc_message: original grpc message
    :return: dict of message
    """
    return {
        field.name: getattr(grpc_message, field.name)
        for field in grpc_message.DESCRIPTOR.fields
    }
