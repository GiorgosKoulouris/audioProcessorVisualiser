"""
================================== USAGE ===============================

Intended Usage (with implemented functionality):
    1. Choose your python interpeter path and source file path
    2. Click "Choose File" to select an audio file to use
    3. Define start and end times (in secs) and
        click "Process Part" to process the selected section
    4. Write your own code for the signal processing and press updateButton
    5. Click the Plot Gain button to show a plot of Gain over Time
        --> checking the checkbutton on the left also
            plots the original and processed signal

===============================================================================
"""
import gc
import os
import subprocess
import sys
import pickle
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Button, Checkbutton

from bloscpack import pack_ndarray_to_file, unpack_ndarray_from_file
from librosa.core import load
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('./')
from Source.exceptions import FilePathException, ScriptReturnCodeException, UserInputExeption
from Source.parameterFrame import ParameterFrame
from Source.renderRangeFrame import RenderRangeFrame


class DspVisualiser:
    def __init__(self) -> None:
        # Interpreter and script related
        self.srcTopLvlPath = os.getcwd() + '/Source'
        self.userCodePath = self.srcTopLvlPath + '/Assets/userCode.py'
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

    # Interpreter and src path related
    # Use to ensure that you dont end up getting symlinks or wrong environments
    def setInterpreterPath(self):
        """
        Display pop-up window to let user set the directory where
        the used python interpreter is
        """
        # TODO: Find a way to get the actual file, not the symlink.
        #   This method involves guessing that user initializes the program
        #   with the same interpreter he is going to provide while using it
        userInput = askdirectory()
        result = userInput + '/python'
        if os.path.isfile(result):
            self.interpreterPath = result
            return True
        else:
            try:
                raise UserInputExeption(
                            "Directory does not contain a python interpreter",
                            error=str(f'Selected Path: {userInput}'))
            except UserInputExeption as e:
                print(e)
                return False

    def setSourceTopLvlDirectory(self):
        """Display pop-up window to let user set the source code directory"""
        self.srcTopLvlPath = askdirectory()

    def initPaths(self):
        """Initializes a wait_window that allows user to set the paths"""
        popUp = Tk()
        popUp.geometry('200x200')
        popUp.title('Configure Setup')

        # FIXME: Canceling on fileChooser causes path abnormalities
        interPathButton = Button(
                                popUp, text='Set interpreter path',
                                command=self.setInterpreterPath)
        srcPathButton = Button(popUp, text='Set source path',
                               command=self.setSourceTopLvlDirectory)

        interPathButton.pack()
        srcPathButton.pack()

        popUp.mainloop()

    # === CodeBlock functions and it's helpers ===

    def setCustomUserScriptPath(self, path=None):
        if path is None:
            tempPath = askopenfilename()
        else:
            tempPath = path

        if tempPath.endswith('.py') and os.path.isfile(tempPath):
            self.userCodePath = tempPath
            return True
        else:
            try:
                raise FilePathException('Invalid path. Should be an existing .py file',
                                        f'Chosen path: {tempPath}')
            except FilePathException as e:
                print(e)

    def updateTextBox(self):
        path = self.userCodePath
        try:
            # Check if file is still there
            if not os.path.isfile(path):
                raise FilePathException('Script path invalid or does not exist',
                                        f'Chosen path: {path}')
            # Copy script's context in TextBox
            with open(path, 'r') as userPy:
                data = userPy.read()
                self.codeBox.delete('1.0', 'end')
                self.codeBox.insert('1.0', data)
                userPy.close()
            return True
        except FilePathException as e:
            print(e)
            return False

    def updateScriptFile(self):
        userIn = self.codeBox.get("1.0", 'end-1c')
        path = self.userCodePath
        with open(path, 'w') as userPy:
            userPy.write(userIn)
            userPy.close()

    # Create or overwrite asset scripts to avoid any errors

    def initAssetScripts(self):
        # Create/Overwrite userCode.py
        codeFilePath = self.srcTopLvlPath + '/Assets/userCode.py'
        with open(codeFilePath, 'w') as userPy:
            userPy.write('import numpy as np\n\n')

            userPy.write(
                'def userCode(input, numChannels, numSamples, sampleRate, p1, p2, p3, p4):\n')
            userPy.write(
                '    # You get an ndarray with a shape of {numChannels, numSamples} as an input\n\n')

            userPy.write(
                '    # p1, p2, p3, p4 are the parameters set by the user.\n')
            userPy.write(
                '    # if P1 is disabled then p1 = 0, so it would be nice to keep an eye on it\n\n')

            userPy.write(
                '    # output is the ndarray that contains your processed data. Must be same shape as input\n')

            userPy.write('    output = input.copy()\n\n')
            userPy.write('    # Your code goes here....\n\n\n\n\n\n')
            userPy.write('    return output\n')

            userPy.close()

        # Create/Overwrite applyUserCode.py
        codeFilePath = self.srcTopLvlPath + '/Assets/applyUserCode.py'
        with open(codeFilePath, 'w') as applyUserPY:
            applyUserPY.write('#!' + self.interpreterPath + '\n\n')
            applyUserPY.write(
                'from bloscpack import unpack_ndarray_from_file, pack_ndarray_to_file\n')
            applyUserPY.write('import pickle\n')   
            applyUserPY.write('import sys\n')
            applyUserPY.write('from userCode import userCode\n\n')

            applyUserPY.write('inS = unpack_ndarray_from_file(sys.argv[1])\n')
            applyUserPY.write('numC = int(sys.argv[2])\n')
            applyUserPY.write('numS = int(sys.argv[3])\n')
            applyUserPY.write('sRate = int(sys.argv[4])\n\n')

            applyUserPY.write('path = sys.argv[5]\n\n')

            applyUserPY.write('with open(path, "rb") as p:\n')
            applyUserPY.write('    pList = pickle.load(p)\n')
            applyUserPY.write('    p.close()\n\n')

            applyUserPY.write(
                'output = userCode(inS, numC, numS, sRate, pList[0], pList[1], pList[2], pList[3])\n\n')
            applyUserPY.write('pack_ndarray_to_file(output, sys.argv[1])\n')

            applyUserPY.close()

    # Choose an audio file

    def chooseFile(self):
        """Display pop-up window to let user select an audio file"""
        # FIXME: Pressing cancel button should not throw an exception
        tempPath = askopenfilename()
        try:
            if tempPath.endswith(".wav"):
                self.importPath = tempPath
                self.fileImported = True
                del tempPath
                return True
            else:
                # If previously selected file was invalid,
                # ensure fileImported is False
                if not self.importPath.endswith('.wav'):
                    self.fileImported = False
                if tempPath != "":
                    raise FilePathException('Not a valid audio file', f'Chosen file: {tempPath}')
        except FilePathException as e:
            print(e)
            return False

    # === Processing function and it's helpers ===

    # Process the audio file

    def processAudio(self, path=None, resampleRate=None, rS=None,
                     rE=None, mono=None):
        """Process the selected range with the given settings"""
        """Range = Start - End
        Resample = True or False (needs new sampleRate if True)
        convertToMono = True or False"""
        # Initialiase errorMsg
        errorMsg = ""
        # TODO: Add resampling options
        if path is None:
            path = self.importPath
            predifinedInput = True
        else:
            predifinedInput = False

        # FIXME: These values should be evaluated seperately
        if rS is None and rE is None and mono is None:
            rS, rE, mono = self.rangeFrame.getValues()
            self.convertToMono = mono

        rangeIsCorrect = (rS >= 0) and (rE > rS)
        try:
            # Check if range is valid
            if not rangeIsCorrect:
                raise UserInputExeption("Invalid time range",
                                        f'Start = {rS} > End = {rE}')

            # Check if it a valid audio file supported
            if predifinedInput and not self.fileImported:
                raise UserInputExeption("No audio file selected",
                    'Define path using the Choose File button or by explicitly passing it as an argument')

            if not predifinedInput and not path.endswith(".wav"):
                raise UserInputExeption(
                    "No valid audio extension (.wav)",
                    f'Given path {path}')

            # ============ Calculating input and variables ==============
            self.durationInSecs = rE - rS
            self.inputS, self.sampleRate = load(self.importPath,
                                                sr=None,
                                                offset=rS,
                                                mono=mono,
                                                duration=self.durationInSecs)

            if mono:
                numChannels = 1
                numSamples = len(self.inputS)
            else:
                numChannels = 2
                numSamples = len(self.inputS[0])
            # User parameters
            par1 = par2 = par3 = par4 = 0
            if self.p1Frame.choice != 0:
                par1 = self.p1Frame.getValue()
            if self.p2Frame.choice != 0:
                par2 = self.p2Frame.getValue()
            if self.p3Frame.choice != 0:
                par3 = self.p3Frame.getValue()
            if self.p4Frame.choice != 0:
                par4 = self.p4Frame.getValue()

            parList = [par1, par2, par3, par4]
            paramListPath = self.srcTopLvlPath + '/Assets/DSPVisParList.dat'
            datFile = open(paramListPath, 'wb')
            pickle.dump(parList, datFile)
            datFile.close()

            # If user used a custom script make sure its context
            # gets copied in the assetscript
            assetScriptPath = self.srcTopLvlPath + '/Assets/userCode.py'
            if self.userCodePath != assetScriptPath:
                if not os.path.isfile(self.userCodePath):
                    raise FilePathException('File path invalid or does not exist',
                                            f'Chosen path: {self.userCodePath}')
                with open(self.userCodePath, 'r') as i:
                    userText = i.read()

                with open(assetScriptPath, 'w') as i:
                    i.write(userText)

            # Save input ndarray as a binary
            scriptPath = self.srcTopLvlPath + '/Assets/applyUserCode.py'

            arrayFilePath = self.srcTopLvlPath + '/Assets/dspVisInputArray.txt'
            pack_ndarray_to_file(self.inputS, arrayFilePath)
            # Run asset scripts
            args = [scriptPath, arrayFilePath, str(numChannels),
                    str(numSamples), str(self.sampleRate),
                    paramListPath]

            processCheck = subprocess.run(args, capture_output=True, text=True)
            if processCheck.returncode != 0:
                raise ScriptReturnCodeException(
                                'Running the audio processing script failed',
                                processCheck.stderr)

            # Delete the reference to the old ndarray
            if self.output is not None:
                del self.output

            self.output = unpack_ndarray_from_file(arrayFilePath)
            # Get rid of any previously created/processed arrays
            gc.collect()
        except UserInputExeption as e:
            errorMsg = e.message
            print(e)
            return False
        except ScriptReturnCodeException as e:
            errorMsg = e.message
            print(e)
            return False
        except FilePathException as e:
            errorMsg = e.message
            print(e)
            return False

    # ================= Plotting functions ======================

    # Plot single waveform

    def plotInWaveform(self, inS=None, isMono=None):
        if isMono is None:
            isMono = self.convertToMono
        if inS is None:
            inS = self.inputS

        if isMono:
            x = np.linspace(0, self.durationInSecs, len(inS))
            fig, ax = plt.subplots(1, 1, num="Single Waveform")
            ax.plot(x, inS, color='g', label="in")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Sample value")
            fig.show()

        del x, fig, ax
        gc.collect()

    # Plot both inputS and output

    def plotStackedWaveforms(self, wave1=None, wave2=None, isMono=None):
        if wave1 is None and wave2 is None:
            wave1 = self.inputS
            wave2 = self.output
            label1 = 'Input'
            label2 = 'Output'
        else:
            label1 = 'WaveForm 1'
            label2 = 'WaveForm 2'

        if isMono is None:
            isMono = self.convertToMono

        if isMono:
            x = np.linspace(0, self.durationInSecs, len(self.inputS))
            fig, ax = plt.subplots(1, 1, num="Stacked Waveforms")
            ax.plot(x, wave1, color='g', label=label1)
            ax.plot(x, wave2, color='b', label=label2)

            fig.show()

            del x, fig, ax
            gc.collect()

    # Function for includeWavesInGainPlotButton

    def setIncludeWavesInGain(self):
        if self.includeWavesInGainPlot:
            self.includeWavesInGainPlot = False
        else:
            self.includeWavesInGainPlot = True

    # Function that calculates gain reduction applied to the signal

    def plotGain(self, inS=None, outS=None, isMono=None):
        """This function plots the gain reduction over time"""
        """If <includeWavesInGainPlot = True>, it also plots
        a stacked overview of the waveforms"""

        # Check if there are arguments passed
        if inS is None:
            inS = self.inputS
        if outS is None:
            outS = self.output
        if isMono is None:
            isMono = self.convertToMono

        if self.fileImported:
            if isMono:
                g = np.zeros(len(inS))

                # FIXME: Fix true_division issue
                for sample in range(len(inS)):
                    if inS[sample] != 0:
                        g[sample] = outS[sample] / inS[sample]
                    else:
                        g[sample] = g[sample - 1]

                x = np.linspace(0, self.durationInSecs, len(inS))

                if self.includeWavesInGainPlot:
                    fig, ax = plt.subplots(
                        2, 1, sharex=True, num="Gain Over Time")
                    ax[0].plot(x, g, color='r', label='Gain Reduction')
                    ax[0].set_ylabel("Gain value")
                    ax[1].plot(x, inS, color='g', label='y1')
                    ax[1].plot(x, outS, color='b', label='y2')
                    ax[1].set_ylabel("Sample value")
                    plt.xlabel("Time (s)")
                    plt.legend()
                    plt.show()
                    del fig, ax, x, g
                    gc.collect()

                else:
                    fig, ax = plt.subplots(1, 1, num="Gain Over Time")
                    ax.plot(x, g, color='r', label='Gain')
                    plt.xlabel("Time (s)")
                    plt.ylabel("Gain Value")
                    plt.legend()
                    plt.show()
                    del fig, ax, x, g
                    gc.collect()

    def initGUI(self, window=None):
        if window is None:
            window = self.mainWindow

        # Main Window
        window.geometry('1200x900')
        window.title('DSP Visualiser')
        window['background'] = '#680118'

        # File Chooser
        self.chooseFileButton = Button(
            window, text='Choose File', command=self.chooseFile)
        self.chooseFileButton.place(x=20, y=10, width=135, height=30)
        # Render Range
        self.rangeFrame = RenderRangeFrame(window)
        self.rangeFrame.draw(20, 50, 150, 50)
        # Parameter frames
        self.p1Frame = ParameterFrame(window, 1)
        self.p1Frame.draw(240, 48, 40, 75)
        self.p2Frame = ParameterFrame(window, 2)
        self.p2Frame.draw(300, 48, 40, 75)
        self.p3Frame = ParameterFrame(window, 3)
        self.p3Frame.draw(360, 48, 40, 75)
        self.p4Frame = ParameterFrame(window, 4)
        self.p4Frame.draw(420, 48, 40, 75)

        # ================= File processing options ===============
        self.processAudioButton = Button(
            window, text='Process Part', command=self.processAudio)
        self.processAudioButton.place(x=20, y=110, width=150, height=25)

        # ===================== Code Entry ====================
        self.codeBox = ScrolledText()
        self.codeBox.place(x=500, y=100, width=670, height=400)

        self.updateTextButton = Button(
            window, text='Update text', command=self.updateTextBox)
        self.updateTextButton.place(x=700, y=520, width=150, height=25)

        self.updateScriptButton = Button(
            window, text='Update script', command=self.updateScriptFile)
        self.updateScriptButton.place(x=530, y=520, width=150, height=25)

        self.setUserScriptPathButton = Button(
            window, text='Choose script path',
            command=self.setCustomUserScriptPath)
        self.setUserScriptPathButton.place(x=870, y=520, width=180, height=25)

        # ===================== Plotting options ====================
        self.includeWavesInGainPlot = False
        self.wavesInGainButton = Checkbutton(
            variable=self.includeWavesInGainPlot,
            command=self.setIncludeWavesInGain)

        self.wavesInGainButton.place(x=50, y=150, width=20, height=20)

        self.plotGainButton = Button(
            window, text='Plot gain over time', command=self.plotGain)
        self.plotGainButton.place(x=120, y=150, width=200, height=35)

    def initiate(self):
        self.initPaths()
        self.mainWindow = Tk()
        self.initGUI()
        self.initAssetScripts()
        self.updateTextBox()
        self.mainWindow.mainloop()
        self.initAssetScripts()


def runApp():
    app = DspVisualiser()
    app.initiate()


if __name__ == '__main__':
    runApp()
