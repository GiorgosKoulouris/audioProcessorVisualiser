import os
import sys
import unittest
from tkinter import Tk
from unittest import mock

import numpy as np
from Source.main import DspVisualiser


class Test_Main(unittest.TestCase):

    # setUp and tearDown
    def setUp(self):
        """
        Create an object and run its __init__ statements so
        they become available for the tests
        """

        self.d = DspVisualiser()

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
    @mock.patch("Source.main.askopenfilename",
                return_value='/my/Random/audioFile.wav')
    def test_chooseFile_behaviourOn_validInput(self, mock_audioFile):
        self.d.importPath = 'old/path.wav'
        self.d.chooseFile()
        expected = '/my/Random/audioFile.wav'
        self.assertEqual(self.d.importPath, expected,
                         'Did not update importPath when input was valid')
        self.assertTrue(self.d.fileImported,
                        'Did not update fileImported when input was valid')

    @mock.patch("Source.main.askopenfilename",
                return_value='/my/invalid/file.mlk')
    def test_chooseFile_behaviourOn_invalidInput(self, mock_audioFile):
        valueBefore = 'legit/audio/file.wav'
        self.d.importPath = valueBefore
        self.d.chooseFile()
        self.assertEqual(self.d.importPath, valueBefore,
                         'Did not update importPath')
        self.assertFalse(self.d.fileImported,
                         'Did not update fileImported when input was valid')

    @mock.patch("Source.main.askopenfilename", return_value='invalid.sth')
    def test_chooseFile_raise_OnInvalidPath(self, mock_audioFile):
        self.assertFalse(self.d.chooseFile())

    @mock.patch('os.path.isfile', return_value=False)
    @mock.patch('Source.main.askdirectory', return_value='some/dir')
    def test_setInterpreterPath_raisedOn_invalidInput(self,
                                                      mock_isFile,
                                                      mock_askdirectory):
        print()
        startValue = 'random/Value'
        self.d.interpreterPath = startValue
        # Should raise
        self.assertFalse(self.d.setInterpreterPath())

    @mock.patch('os.path.isfile', return_value=False)
    @mock.patch('Source.main.askdirectory', return_value='some/dir')
    def test_setInterpreterPath_rejectNewValueOn_invalidInput(
            self, mock_isFile, mock_askdirectory):

        print()
        startValue = 'random/Value'
        self.d.interpreterPath = startValue
        self.d.setInterpreterPath()
        # Should not change value
        self.assertEqual(self.d.interpreterPath, startValue)

    @mock.patch('Source.main.pack_ndarray_to_file',
                return_value=True,
                autospec=True)
    @mock.patch('Source.main.unpack_ndarray_from_file',
                return_value=[324, 234, 5],
                autospec=True)
    def test_processAudio_raiseOn_invalidInput(self, mock_pack, mock_unpack):

        argset = [['invalid.rew', None, 1, 2, True],
                  ['valid.wav', None, 2, 1, True]]
        print()

        for i in range(len(argset)):
            self.d.srcTopLvlPath = 'random/path'
            with self.subTest():
                arg = argset[i]
                print(f'Test No {i}')
                print(f'Arguments: {arg}')
                self.assertFalse(self.d.processAudio(arg[0], arg[1], arg[2],
                                                     arg[3], arg[4]))

    @mock.patch('Source.main.pack_ndarray_to_file')
    @mock.patch('Source.main.unpack_ndarray_from_file')
    @mock.patch('Source.main.load',
                side_effect=None,
                return_value=([1, 2, 3, 4], 4434))
    def test_processAudio_exceptionsHandled(self,
                                            mock_load,
                                            mock_unpack, mock_pack):

        argset = [['invalid.rew', None, 1, 2, True],
                  ['valid.wav', None, 2, 1, True]]
        print()

        for i in range(len(argset)):
            self.d.srcTopLvlPath = 'invalid/path'
            with self.subTest():
                arg = argset[i]
                print(f'Test No {i}')
                print(f'Arguments: {arg}')
                self.d.processAudio(arg[0], arg[1], arg[2], arg[3], arg[4])

    @mock.patch('Source.main.pack_ndarray_to_file')
    @mock.patch('Source.main.unpack_ndarray_from_file',
                return_value=[1, 2, 3, 4])
    @mock.patch('Source.main.load',
                side_effect=None,
                return_value=([1, 2, 3, 4], 4434))
    def test_processAudio_rejectedProcessingAudio_invalidInput(self,
                                                               mock_load,
                                                               mock_unpack,
                                                               mock_pack):
        # FIXME: mock RangeFrame.getValues() to isolate the test
        argset = [['invalid.rew', None, 1, 2, True],
                  ['valid.wav', None, 2, 1, True]]
        print()
        for i in range(len(argset)):
            self.d.mainWindow = Tk()
            self.d.initGUI()
            initialBuffer = [0, 0, 0, 0]
            self.d.inputS = initialBuffer
            with self.subTest():
                arg = argset[i]
                print(f'Test No {i}')
                print(f'Arguments: {arg}')
                self.d.processAudio(arg[0], arg[1], arg[2], arg[3], arg[4])
                self.assertEqual(self.d.inputS, initialBuffer)

    @mock.patch('Source.main.pack_ndarray_to_file')
    @mock.patch('Source.main.unpack_ndarray_from_file',
                return_value=[1, 2, 3, 4])
    @mock.patch('Source.main.load',
                side_effect=None,
                return_value=([1, 2, 3, 4], 4434))
    def test_processAudio_processedAudioOn_validInputs(self,
                                                       mock_load,
                                                       mock_unpack,
                                                       mock_pack):
        # FIXME: mock RangeFrame.getValues() to isolate the test
        argset = [['valid.wav', None, 1, 2, True],
                  ['valid.wav', None, 4, 12, True]]
        print()
        for i in range(len(argset)):
            self.d.mainWindow = Tk()
            self.d.initGUI()
            initialBuffer = [0, 0, 0, 0]
            self.d.inputS = initialBuffer
            with self.subTest():
                arg = argset[i]
                print(f'Test No {i}')
                print(f'Arguments: {arg}')
                self.d.processAudio(arg[0], arg[1], arg[2], arg[3], arg[4])
                self.assertEqual(self.d.inputS, [1, 2, 3, 4])


if __name__ == '__main__':
    unittest.main()
