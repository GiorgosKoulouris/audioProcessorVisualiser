#!/Users/cliff/plugin-development/Python/audioProcessorVisualiser/venv/bin/python3.7

from bloscpack import unpack_ndarray_from_file, pack_ndarray_to_file
import pickle
import sys
from userCode import userCode

inS = unpack_ndarray_from_file(sys.argv[1])
numC = int(sys.argv[2])
numS = int(sys.argv[3])
sRate = int(sys.argv[4])

path = sys.argv[5]

with open(path, "rb") as p:
    pList = pickle.load(p)
    p.close()

output = userCode(inS, numC, numS, sRate, pList[0], pList[1], pList[2], pList[3])

pack_ndarray_to_file(output, sys.argv[1])
