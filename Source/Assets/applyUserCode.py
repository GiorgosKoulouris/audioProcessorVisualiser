#!/Users/cliff/plugin-development/Python/audioProcessorVisualiser/venv/bin/python3.7

from bloscpack import unpack_ndarray_from_file, pack_ndarray_to_file
import sys
from userCode import userCode

inS = unpack_ndarray_from_file(sys.argv[1])
numC = int(sys.argv[2])
numS = int(sys.argv[3])
sRate = int(sys.argv[4])
par1 = sys.argv[5]
par2 = sys.argv[6]
par3 = sys.argv[7]
par4 = sys.argv[8]

output = userCode(inS, numC, numS, sRate, par1, par2, par3, par4)

pack_ndarray_to_file(output, sys.argv[1])
