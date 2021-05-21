import unittest
import sys
sys.path.append('./Source')

import numpy as np
from Source.main import plotGain


class Test_Main(unittest.TestCase):
    def test_plotGain(self):
        plotGain


if __name__ == '__main__':
    unittest.main()
