"""
Client gRPC services for running on FPGA reservoir computer EmuCore developed by QCi.
"""
import logging
import json
import time
from typing import List, TypedDict
import os
import grpc
from grpc._channel import _InactiveRpcError
import numpy as np
from . import emucore_pb2, emucore_pb2_grpc
from .utils import set_filter_coefficients, \
    bytes_to_array, \
    prep_input_data, \
    message_to_dict

grpc_service_config = json.dumps(
    {
        "methodConfig": [
            {
                "name": [{"service": "EmuCore.EmuCoreService"}],
                "retryPolicy": {
                    "maxAttempts": 5, # this is the max number of attempts
                    "initialBackoff": "0.2s",
                    "maxBackoff": "10s",
                    "backoffMultiplier": 2.5,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            }
        ]
    }
)

MAX_INPUT_SIZE = 20*1024*1024
# Why is it set to this length?
# modifies Electro-Optical Modulator (EOM) coefs

class StatusMessage(TypedDict):
    """
    Structure of responses for configuration requests to EmuCore device.
    
    :param status: the status of the request
    :param message: a description for the recieved status
    """
    status: int
    message: str




class InactiveRpcError(Exception):
    """Custom exception wrapper around grpc._channel._InactiveRpcError."""


class EmuCoreClient:
    """
    Provides services for accessing EmuCore server

    :param ip_addr: the IP address of the gRPC server
    :param port:
        The port that the RPC server is running on
    :param max_data_size: int
        The max send and recieve message length for RPC server

    .. note::

       :code:`lock_id` is used by a variety of class functions.
       It is set to an empty string by default since default for device server
       :code:`lock_id` is also an empty string. This allows for single user
       processing without having to acquire a device lock.

    .. All GRPC calls follow a specific pattern:
    ..   1. Fill in data to be sent in message stub
    ..   2. Send data using stub service method
    ..   3. Parse response
    """
    def __init__(
        self,
        ip_addr: str = os.getenv("DEVICE_IP_ADDRESS", "localhost"),
        port: str = os.getenv("DEVICE_PORT", "50051"),
        max_data_size: int =512 * 1024 * 1024,
    ):
        self._ip_add_port = ip_addr + ":" + port
        self._channel_opt = [
            ("grpc.max_send_message_length", max_data_size),
            ("grpc.max_receive_message_length", max_data_size),
            ("grpc.service_config", grpc_service_config),
        ]
        self.channel = grpc.insecure_channel(
            self._ip_add_port, options=self._channel_opt
        )
        self.stub = emucore_pb2_grpc.EmuCoreServiceStub(self.channel)

    def check_lock(self, lock_id: str = "") -> dict:
        """
        Checks if submitted :code:`lock_id` has execution lock on the device

        :param lock_id: a UUID which will be checked to determine if has exclusive
            device execution lock
        :return: a dict with following keys:

           - **status_code**: `int`- status code for lock check
           - **status_desc**: `str`- a description for the associated status code
        """
        check_input = emucore_pb2.lock_message(lock_id=lock_id)
        check_output = self.stub.check_lock(check_input)
        return message_to_dict(check_output)


    def reservoir_reset(self,
                        lock_id) -> StatusMessage:
        """
        Resets a reservoir instance by clearing RAM on the server

        :param lock_id: a lock_id which has an active reserve on the device
        
        :return: 
           dictionary with with values from members of
           :class:`emucore_direct.types.StatusResponses`
        """
        reset_message = emucore_pb2.lock_message(lock_id=lock_id)
        return message_to_dict(self.stub.reservoir_reset(reset_message))

    def system_info(self) -> dict:
        """
        Provides system info on call
        
        :return: 
           dict with following keys:

           - **system_name**: `str`- product name
           - **system_version**: `str`- server version
           
        """
        sys_info_resp = self.stub.system_info(emucore_pb2.empty_message())
        return message_to_dict(sys_info_resp)
    
    def acquire_lock(self) -> dict:
        """
        Attempts to acquire exclusive lock for submitting jobs

        :return:
           a member of :class:`emucore_direct.types.LockManageStatus` as a dict along
           with an additional key :code:`lock_id`:

           - **lock_id**: `str`- if acquired the current device `lock_id`
             else empty string
           - **status**: `int`- status code for lock id acquisition
           - **message**: `str`- a description for the associated status code
        """
        try:
            acquire_lock_resp = self.stub.acquire_lock(emucore_pb2.empty_message())
        except _InactiveRpcError as exc:
            raise InactiveRpcError(
                "acquire_lock failed due to grpc._channel._InactiveRpcError."
            ) from exc
        return message_to_dict(acquire_lock_resp)

    def release_lock(self, lock_id):
        """
        Releases exclusive lock for submitting data to reservoir

        :param lock_id: a UUID with currently acquired exclusive device lock
        :return: 
           a dict with the following keys:

           - **lock_released**: `bool`- if released is True else False
           - **message**: `str`- a description of release operation result
        """
        release_input = emucore_pb2.lock_message(lock_id = lock_id)
        try:
            release_lock_resp = self.stub.release_lock(release_input)
        except _InactiveRpcError as exc:
            raise InactiveRpcError(
                "release_lock failed due to grpc._channel._InactiveRpcError."
            ) from exc
        return message_to_dict(release_lock_resp)
    
    def rc_config(self,
               lock_id: str,
               vbias: float,
               gain: float,
               num_nodes: int,
               num_taps: int) -> StatusMessage:
        """
        Configures reservoir model and how data will be processed by the reservoir.

        :param lock_id: a lock_id which has an active reserve on the device
        :param vbias: bias to apply to each node in reservoir. Range for parameter [0,1].
        :param gain: memory setting for system how long should inputs effect reservoir similar
               to beta in adaptive gradient descent range for parameter [0,1]
        :param num_nodes: the total number of hidden nodes to instantiate within the reservoir,
               a single hidden layer
        :param num_taps: number of connections in reservoir, generally should be set to less
           than the number of nodes in reservoir. Defines interconnection between nodes.
        :return: dictionary with with values from one of the members of
              :class:`emucore_direct.types.StatusResponses`           
        """
        filter_coefs = set_filter_coefficients(num_taps=num_taps)
        config_message = emucore_pb2.rc_config_message(lock_id=lock_id,
                                                   vbias = vbias,
                                                   gain = gain,
                                                   num_nodes = num_nodes,
                                                   num_taps = num_taps)
        rc_status = self.stub.rc_config(config_message)
        return message_to_dict(rc_status)
            



    def rc_run(self,
               lock_id: str,
               reservoir_input: List[int],):
        """
        Runs a series of data through the reservoir and returns response from device
        based on current reservoir configuration.

        :param lock_id: a lock_id which has an active reserve on the device
        :param reservoir_input: a list of digitized values to input to the reservoir must be
               less than MAX_INPUT_SIZE
        :return: a dictionary with the folowing keys:

           - **status**: `int`- the status for the reservoir submission
           - **message**: `str`- a description of the status for the submission
           - **states**: `bytes`- response from reservoir as bytes.
        """
        assert MAX_INPUT_SIZE>=len(reservoir_input), \
            f"Input to reservoir must be of less than or equal to {MAX_INPUT_SIZE} was {len(reservoir_input)}"
        run_message = emucore_pb2.rc_run_message(lock_id=lock_id,
                                                   input = reservoir_input,)
        rc_response = self.stub.rc_run(run_message)
        return message_to_dict(rc_response)
            

    def wait_for_lock(self):
        """
        Waits for lock indefinitely calling :func:`acquire_lock`

        :return: a tuple of the following items:

           - **lock_id**: `str`- exclusive lock for device execution with a timeout
           - **start_queue_ts**: `int`- time in ns when began lock acquisition.
           - **end_queue_ts**: `int`- time in ns when lock was acquired.
        """
        lock_id = ""
        start_queue_ts = time.time_ns()
        while lock_id == "":
            lock_id = self.acquire_lock()["lock_id"]
            # only sleep if didn't get lock on device
            if lock_id == "":
                time.sleep(1)
        end_queue_ts = time.time_ns()
        return lock_id, start_queue_ts, end_queue_ts        
    
    def process_all_data(self,
                         lock_id: str,
                         input_data: np.ndarray,
                         num_nodes: int,
                         density: float,
                         feature_scaling: float,
                         max_scale_val: float=None,
                         weights: np.ndarray=None,
                         seed_val_weights: int=13):
        """
        Run dataset through reservoir:

        1. Get lock
        2. Apply scaling and random weights mask to input data
        3. Run data through reservoir
        4. Combine data from reservoir responses and reshape based on number of nodes
        5. Release lock

        :param lock_id: a UUID that currently has lock on the device
        :param input_data: data or series to process via reservoir
        :param num_nodes: the total number of hidden nodes to instantiate within the reservoir,
            a single hidden layer (this is also used to apply random weights to to the data
            as well as reshape data recieved from reservoir back to correct output dimension)
        :param feature_scaling: after applying max abs scalar feature scaling factor applied 
        :param max_scale_val: max absolute value used to scale data if provided
        :param seed_val_weights: seeds randomness for weigths to allow for reproducibility
        :note: if doing multiple runs without reset the max value mustn't exceed original
            data max value in order for results to be processed properly. 

        :return:
           a tuple of the following elements:
           
           - **reservoir_response**: `np.ndarray`- reservoir response represented as an array dimension of array will be nrows of input matrix by num nodes.
           - **max_scale_value**: `np.ndarray`- the scaling value that was applied to the input data before it was processed by the reservoir.
           - **weights**: `np.ndarray`- the weights that were used to apply the random mask to the data prior to being processed by the reservoir.
        """
        n_rows, n_cols = input_data.shape
        input_packets, max_scale_val, weights = prep_input_data(
            input_data=input_data,
            num_nodes=num_nodes,
            density=density,
            feature_scaling=feature_scaling,
            max_scale_val=max_scale_val,
            weights=weights,
            seed_val_weights=seed_val_weights)
        try:
            reservoir_resp = np.array([])
            for i in input_packets:
                packet_resp = self.rc_run(
                    lock_id=lock_id,
                    reservoir_input=i)
                packet_bytes = bytearray(np.array(packet_resp["states"]))            
                packet_arr = bytes_to_array(input_bytes=packet_bytes)
                reservoir_resp = np.concatenate((reservoir_resp, packet_arr),axis=0)
        except Exception as err:
            print("ERROR OCCURRED", err)
            raise RuntimeError("Error while processing data") from err
        return np.array(reservoir_resp).reshape(n_rows,num_nodes), max_scale_val, weights
