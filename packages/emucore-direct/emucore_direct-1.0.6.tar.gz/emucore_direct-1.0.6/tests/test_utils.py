import unittest
import os
from emucore_direct.utils import *
import numpy as np
import time

class TestUtils(unittest.TestCase):
    def test_set_filter_coefficients(self):
        """
        Will be moved ot server sided so testing will happen there later
        """
        filt_coefs = set_filter_coefficients(num_taps=10)
        # filt coefs are filled in reverse order in list
        # so start check at end
        self.assertTrue(np.all(filt_coefs[-10:]!=0))
        self.assertTrue(np.all(filt_coefs[:-11]==0))
