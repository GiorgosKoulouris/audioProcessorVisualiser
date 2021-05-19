#!/Users/cliff/plugin-development/Python/pythonAudioHelper/venv/bin/python

import pickle
import numpy as np
import sys
from userCode import userCode

intS = pickle.loads(sys.argv[1])
outS = pickle.loads(sys.argv[2])
numC = int(sys.argv[3])
numS = int(sys.argv[4])
sRate = int(sys.argv[5])
par1 = sys.argv[6]
par2 = sys.argv[7]
par3 = sys.argv[8]
par4 = sys.argv[9]

def getOut():
    result = userCode(intS, outS, numC, numS, sRate, par1, par2, par3, par4)
    return result

getOut()
