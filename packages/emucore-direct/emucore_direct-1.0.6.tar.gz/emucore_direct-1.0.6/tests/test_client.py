"""
Relies on environment var RC_DEVICE_IP_ADDRESS to identify IP_ADDRESS FOR tests
"""
import unittest
import os
from emucore_direct.client import EmuCoreClient, MAX_INPUT_SIZE
import numpy as np
import time

class TestEmucoreClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_ip_addr = os.getenv("RC_DEVICE_IP_ADDRESS")
        print("Testing client against IP ADDRESS:", test_ip_addr)
        cls.ec_client = EmuCoreClient(ip_addr=test_ip_addr)
        cls.input_long = np.random.normal(size = (3,4))

    def test_basic_locking(self):
        print("Test basic locking")
        lock_id = self.ec_client.acquire_lock()["lock_id"]
        try:
            if lock_id!="":
                print("Lock id", lock_id)
                self.assertIsInstance(lock_id, str)
                self.assertEqual(36, len(lock_id))
        finally:
            release_out = self.ec_client.release_lock(lock_id=lock_id)
        print("RELEASE LOCK MSG", release_out)
        self.assertEqual(release_out["status"], 0)
        self.assertEqual(release_out["message"], 'Success')

    def test_wait_for_lock(self):
        print("Test wait for lock")
        lock_id, start_ts, end_ts = self.ec_client.wait_for_lock()
        try:
            self.assertIsInstance(lock_id, str)
            self.assertEqual(36, len(lock_id))
            self.assertTrue(start_ts<end_ts)
            self.assertIsInstance(start_ts, int)
            self.assertIsInstance(end_ts, int)
        finally:
            self.ec_client.release_lock(lock_id=lock_id)



    def test_rc_config(self):
        print("RC CONFIG")
        lock_id, start_ts, end_ts = self.ec_client.wait_for_lock()
        try:
            resp = self.ec_client.rc_config(lock_id = lock_id,
                                            vbias = 0.3,
                                            gain = 0.7,
                                            num_nodes = 500,
                                            num_taps = 250)
            print("CONFIG MSG", resp)
            self.assertEqual(resp["status"], 0)
            self.assertEqual(resp["message"], "Success")
        finally:
            self.ec_client.release_lock(lock_id=lock_id)

    def test_rc_run(self):
        print("Test rc_run")
        lock_id, start_ts, end_ts = self.ec_client.wait_for_lock()
        try:
            print("Lock ID", lock_id)
            rc_big = np.random.randint(0,10000, size = MAX_INPUT_SIZE+1).tolist()
            with self.assertRaises(AssertionError):
                self.ec_client.rc_run(
                    lock_id=lock_id,
                    reservoir_input = rc_big,
                )
        finally:
            self.ec_client.release_lock(lock_id=lock_id)


    #def test_process_all(self):
        
