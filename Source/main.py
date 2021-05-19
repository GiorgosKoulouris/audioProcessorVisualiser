"""
================================== USAGE ===============================

Intended Usage (with implemented functionality):
    1. Click "Choose File" to select an audio file to use
    2. Define start and end times (in secs) and click "Process Part" to process the selected section
    3. Write your own code for the signal processing and press updateButton
    2. Click the Plot Gain button to show a plot of Gain over Time
        --> checking the checkbutton on the left also plots the original and processed signal

===============================================================================
"""
import sys

import librosa as lr
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Toplevel
from tkinter.ttk import Button, Checkbutton
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.scrolledtext import ScrolledText
import gc, os
from parameterFrame import ParameterFrame
from renderRangeFrame import RenderRangeFrame
import bloscpack as bp
import subprocess


# ================ Global Variables =====================
# Interpreter and script related
interpreterPath = sys.executable
srcTopLvlPath = os.getcwd()

# Audio file related
fileImported = False
importPath = "~/Desktop"

# File and Signal related
sampleRate = 44100
convertToMono = False
inputS = np.zeros(sampleRate)
durationInSecs = 1
numChannels = 2
numSamples = sampleRate
output = inputS.copy

# Plotting options
includeWavesInGainPlot = False

mainWindow = Tk()

# =================== Function Definitions =================
# Interpreter and src path related
def setInterpreterPath():
    """Display pop-up window to let user set the directory where the used python interpreter is"""
    """We ask for the bin directory instead of the python executable. This happens because in most venvs python
    executables are a symlink to the a preinstalled python env. Having that as our interpreter would cause some
    library missing errors whe it comes to executing the asset scripts"""
    # TODO: Find a way to get the actual file, not the symlink. This method involves guessing that user initializes
    #     the program with the same interpreter he is going to provide while using it
    global interpreterPath
    interpreterPath = askdirectory() + '/python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor)

def setSourceTopLvlDirectory():
    """Display pop-up window to let user set the source code directory"""
    global srcTopLvlPath
    srcTopLvlPath = askdirectory()

def initPaths():
    """Initializes a wait_window that allows user to set the paths"""
    popUp = Toplevel(mainWindow)
    popUp.geometry('200x200')
    popUp.title('Configure Setup')

    interPathButton = Button(popUp, text='Set interpreter path', command=setInterpreterPath)
    srcPathButton = Button(popUp, text='Set source path', command=setSourceTopLvlDirectory)

    interPathButton.pack()
    srcPathButton.pack()

    popUp.wait_window()

# Choose an audio file
def chooseFile():
    """Display pop-up window to let user select an audio file"""
    tempPath = askopenfilename()
    if tempPath.endswith(".wav"):
        global importPath
        importPath = tempPath
        global fileImported
        fileImported = True
    del tempPath

# === Processing function and it's helpers ===

# Process the audio file
def processAudio():
    """Process the selected range with the given settings"""
    """Range = Start - End
    Resample = True or False (needs new sampleRate if True)
    convertToMono = True or False"""
    # TODO: Add resampling options
    global convertToMono
    rS, rE, convertToMono = rangeFrame.getValues()

    rangeIsCorrect = (rS >= 0) and (rE > rS)
    if rangeIsCorrect and fileImported:
        global sampleRate
        global inputS
        global durationInSecs
        global output
        global numChannels
        global numSamples

        del inputS

        # ============ Calculating input and variables ==============
        durationInSecs = rE - rS
        inputS, sampleRate = lr.load(importPath, sr=None, offset=rS, mono=convertToMono, duration=durationInSecs)

        if convertToMono:
            numChannels = 1
            numSamples = len(inputS)
        else:
            numChannels = 2
            numSamples = len(inputS[0])

        # User parameters
        par1 = par2 = par3 = par4 = 0
        global p1Frame
        global p2Frame
        global p3Frame
        global p4Frame
        if p1Frame.choice != 0:
            par1 = p1Frame.getValue()
        if p2Frame.choice != 0:
            par2 = p2Frame.getValue()
        if p3Frame.choice != 0:
            par3 = p3Frame.getValue()
        if p4Frame.choice != 0:
            par4 = p4Frame.getValue()

        # Save input ndarray as a binary
        scriptPath = srcTopLvlPath + '/Assets/applyUserCode.py'
        arrayFilePath = srcTopLvlPath + '/Assets/dspVisInputArray.txt'
        bp.pack_ndarray_to_file(inputS, arrayFilePath)

        # Run asset scripts
        args = [scriptPath, arrayFilePath, str(numChannels), str(numSamples), str(sampleRate), str(par1), str(par2), str(par3), str(par4)]
        processCheck = subprocess.run(args, capture_output=True, text=True)

        # Check for errors and receive processed signal
        if processCheck.returncode == 0:
            global output
            del output
            output = bp.unpack_ndarray_file(arrayFilePath)
        else:
            # TODO: This should instead initialize a popup window displaying the error message
            print(processCheck.stderr)

        # Get rid of any previously created/processed arrays
        gc.collect()

# === customCode functions and it's helpers ===
def updateCodeBlock():
    userIn = codeBox.get("1.0", 'end-1c')
    codeFilePath = srcTopLvlPath + '/Assets/userCode.py'
    with open(codeFilePath, 'w') as userPy:
        userPy.write(userIn)
        userPy.close()

# Create or overwrite asset scripts to avoid any errors
def createAssetScripts():
    # Create/Overwrite userCode.py
    codeFilePath = srcTopLvlPath + '/Assets/userCode.py'
    with open(codeFilePath, 'w') as userPy:
        userPy.write('import numpy as np\n\n')

        userPy.write('def userCode(input, numChannels, numSamples, sampleRate, p1, p2, p3, p4):\n')
        userPy.write('    # You get an ndarray with a shape of {numChannels, numSamples} as an input\n\n')

        userPy.write('    # p1, p2, p3, p4 are the parameters set by the user.\n')
        userPy.write('    # if P1 is disabled then p1 = 0, so it would be nice to keep an eye on it\n\n')

        userPy.write('    # output is the ndarray that contains your processed data. Must be same shape as input\n')

        userPy.write('    output = input.copy()\n\n')
        userPy.write('    # Your code goes here....\n\n\n\n\n\n')
        userPy.write('    return output\n')

        userPy.close()

    # Create/Overwrite applyUserCode.py
    codeFilePath = srcTopLvlPath + '/Assets/applyUserCode.py'
    with open(codeFilePath, 'w') as applyUserPY:
        applyUserPY.write('#!' + interpreterPath + '\n\n')
        applyUserPY.write('import bloscpack as bp\n')
        applyUserPY.write('import sys\n')
        applyUserPY.write('from userCode import userCode\n\n')

        applyUserPY.write('inS = bp.unpack_ndarray_file(sys.argv[1])\n')
        applyUserPY.write('numC = int(sys.argv[2])\n')
        applyUserPY.write('numS = int(sys.argv[3])\n')
        applyUserPY.write('sRate = int(sys.argv[4])\n')
        applyUserPY.write('par1 = sys.argv[5]\n')
        applyUserPY.write('par2 = sys.argv[6]\n')
        applyUserPY.write('par3 = sys.argv[7]\n')
        applyUserPY.write('par4 = sys.argv[8]\n\n')

        applyUserPY.write('output = userCode(inS, numC, numS, sRate, par1, par2, par3, par4)\n\n')
        applyUserPY.write('bp.pack_ndarray_to_file(output, sys.argv[1])\n')

        applyUserPY.close()

def updateCodeBox():
    codeFilePath = srcTopLvlPath + '/Assets/userCode.py'
    with open(codeFilePath, 'r') as userPy:
        data = userPy.read()
        codeBox.insert('1.0', data)
        userPy.close()

# ================= Plotting functions ======================

# Plot single waveform
def plotInWaveform():
    global inputS
    if convertToMono:
        x = np.linspace(0, durationInSecs, len(inputS))
        fig, ax = plt.subplots(1, 1, num="Single Waveform")
        ax.plot(x, inputS, color='g', label="in")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Sample value")
        fig.show()

    del x, fig, ax
    gc.collect()

# Plot both inputS and output
def plotStackedWaveforms():
    if convertToMono:
        x = np.linspace(0, durationInSecs, len(inputS))
        fig, ax = plt.subplots(1, 1, num="Stacked Waveforms")
        ax.plot(x, inputS, color='g', label='inputS')
        ax.plot(x, output, color='b', label='Output')

        fig.show()

        del x, fig, ax
        gc.collect()

# Function for includeWavesInGainPlotButton
def setIncludeWavesInGain():
    global includeWavesInGainPlot
    if includeWavesInGainPlot:
        includeWavesInGainPlot = False
    else:
        includeWavesInGainPlot = True

# Function that calculates gain reduction applied to the signal
def plotGain():
    """This function plots the gain reduction over time"""
    """If <includeWavesInGainPlot = True>, it also plots a stacked overview of the waveforms"""
    if fileImported:
        if convertToMono:
            g = np.zeros(len(inputS))

            # FIXME: Fix true_division issue
            for sample in range(len(inputS)):
                if inputS[sample] != 0:
                    g[sample] = output[sample] / inputS[sample]
                else:
                    g[sample] = g[sample - 1]

            x = np.linspace(0, durationInSecs, len(inputS))

            if includeWavesInGainPlot:
                fig, ax = plt.subplots(2, 1, sharex=True, num="Gain Over Time")
                ax[0].plot(x, g, color='r', label='Gain Reduction')
                ax[0].set_ylabel("Gain value")
                ax[1].plot(x, inputS, color='g', label='y1')
                ax[1].plot(x, output, color='b', label='y2')
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


# ========== App loop =============


# Main Window
mainWindow.geometry('1200x900')
mainWindow.title('DSP Visualiser')
mainWindow['background'] = '#680118'
initPaths()


# ============================== GUI ========================
# File Chooser
chooseFileButton = Button(mainWindow, text='Choose File', command=chooseFile)
chooseFileButton.place(x=20, y=10, width=135, height=30)
# Render Range
rangeFrame = RenderRangeFrame(mainWindow)
rangeFrame.draw(20, 50, 150, 50)
# Parameter frames
p1Frame = ParameterFrame(mainWindow, 1)
p1Frame.draw(240, 48, 40, 75)
p2Frame = ParameterFrame(mainWindow, 2)
p2Frame.draw(300, 48, 40, 75)
p3Frame = ParameterFrame(mainWindow, 3)
p3Frame.draw(360, 48, 40, 75)
p4Frame = ParameterFrame(mainWindow, 4)
p4Frame.draw(420, 48, 40, 75)

# ================= File processing options ===============
processAudioButton = Button(mainWindow, text='Process Part', command=processAudio)
processAudioButton.place(x=20, y=110, width=150, height=25)

# ===================== Code Entry ====================
codeBox = ScrolledText()
codeBox.place(x=500, y=100, width=670, height=400)
updateCodeButton = Button(mainWindow, text='Update code', command=updateCodeBlock)
updateCodeButton.place(x=675, y=520, width=220, height=25)

# ===================== Plotting options ====================
includeWavesInGainPlot = False
wavesInGainButton = Checkbutton(variable=includeWavesInGainPlot, command=setIncludeWavesInGain)
wavesInGainButton.place(x=50, y=150, width=20, height=20)

plotGainButton = Button(mainWindow, text='Plot gain over time', command=plotGain)
plotGainButton.place(x=120, y=150, width=200, height=35)

# Create customCodeFile
createAssetScripts()
updateCodeBox()

# ===============================================
# start App
mainWindow.mainloop()
# Recreate the file so upon next import there are no errors if user misspells sth
createAssetScripts()
