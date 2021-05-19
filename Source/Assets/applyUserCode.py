#!/Users/cliff/plugin-development/Python/pythonAudioHelper/venv/bin/python3.7

import bloscpack as bp
import sys
from userCode import userCode

inS = bp.unpack_ndarray_file(sys.argv[1])
numC = int(sys.argv[2])
numS = int(sys.argv[3])
sRate = int(sys.argv[4])
par1 = sys.argv[5]
par2 = sys.argv[6]
par3 = sys.argv[7]
par4 = sys.argv[8]

def getOut():
    result = userCode(inS, numC, numS, sRate, par1, par2, par3, par4)
    return result

getOut()
