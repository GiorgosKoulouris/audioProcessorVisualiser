import os
import sys
import unittest
from tkinter import Tk
from unittest import mock

import numpy as np
from Source.main import DspVisualiser
from Source.exceptions import *


class Test_Main(unittest.TestCase):

    # setUp and tearDown
    def setUp(self):
        # create an object and run its __init__ statements so they become available for the tests

        self.d = DspVisualiser()
        """
        # Interpreter and script related
        self.d.srcTopLvlPath = os.getcwd() + '/Source'
        self.d.interpreterPath = sys.executable

        # Audio file related
        self.d.fileImported = False
        self.d.importPath = "~/Desktop"

        # File and Signal related
        self.d.sampleRate = 44100
        self.d.convertToMono = False
        self.d.inputS = np.zeros(self.d.sampleRate)
        self.d.durationInSecs = 1
        self.d.numChannels = 2
        self.d.numSamples = self.d.sampleRate
        self.d.output = self.d.inputS.copy()

        # Plotting options
        self.d.includeWavesInGainPlot = False        
        """

        # Interpreter and script related
        self.srcTopLvlPath = os.getcwd() + '/Source'
        self.interpreterPath = sys.executable

        # Audio file related
        self.fileImported = False
        self.importPath = "~/Desktop"

        # File and Signal related
        self.sampleRate = 44100
        self.convertToMono = False
        self.inputS = np.zeros(self.sampleRate)
        self.durationInSecs = 1
        self.numChannels = 2
        self.numSamples = self.sampleRate
        self.output = self.inputS.copy()

        # Plotting options
        self.includeWavesInGainPlot = False

    def tearDown(self):
        del self.d

    #  =============== Tests =================

    # =============== initGUI method =================

    def test_initGUI_customParentOK(self):
        customWindow = Tk()
        self.d.initGUI(customWindow)
        self.assertEqual(self.d.p1Frame.parent, customWindow,
                         'Parent is not passed correctly')

    def test_initGUI_defaultParentOK(self):
        self.d.mainWindow = Tk()
        self.d.initGUI()
        self.assertEqual(self.d.p2Frame.parent, self.d.mainWindow, 
                         'mainWindow as default parent of GUI not passed correctly')

    # =============== chooseFile method =================
    @mock.patch("Source.main.askopenfilename", return_value='/my/Random/audioFile.wav')
    def test_chooseFile_capturedValidPath(self, mock_audioFile):
        self.d.chooseFile()
        expected = '/my/Random/audioFile.wav'
        self.assertEqual(self.d.importPath, expected, 'Did not update importPath')

    @mock.patch("Source.main.askopenfilename", return_value='/my/Random/notAudioFile.sth')
    def test_chooseFile_raise_OnInvalidPath(self, mock_audioFile):
        with self.assertRaises(Exception, msg='Not raised when file was not an audio file'):
            self.d.chooseFile()






if __name__ == '__main__':
    unittest.main()
