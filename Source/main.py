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
import tkinter
import librosa as lr
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.ttk import Button, Label, Entry, Checkbutton
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
import gc, os
from parameterFrame import ParameterFrame
from Assets.userCode import userCode

# ================ Global Variables =====================
# Path
fileImported = False
importPath = "~/Desktop"

# File and Signal related
sampleRate = 44100
convertToMono = False
inputS = np.zeros(sampleRate)
startTime = 0
endTime = 4
durationInSecs = endTime - startTime
output = inputS.copy

# Plotting options
includeWavesInGainPlot = False

# =================== Function Definitions =================

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
# setMonoButton command
def setMonoConversion():
    global convertToMono
    if convertToMono:
        convertToMono = False
    else:
        convertToMono = True

# Process the audio file
def processAudio():
    """Process the selected range with the given settings"""
    """Range = Start - End
    Resample = True or False (needs new sampleRate if True)
    convertToMono = True or False"""
    rS = int(startTime.get())
    rE = int(endTime.get())
    rangeIsCorrect = (rS >= 0) and (rE > rS)
    if rangeIsCorrect and fileImported:
        global sampleRate
        global inputS
        global durationInSecs
        global output

        del inputS
        gc.collect()

        durationInSecs = rE - rS
        inputS, sampleRate = lr.load(importPath, sr=None, offset=rS, mono=convertToMono, duration=durationInSecs)

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

        global output
        del output
        output = inputS.copy()
        userCode(inputS, output, 1, len(inputS), sampleRate, par1, par2, par3, par4)


# === customCode functions and it's helpers ===
def applyCustomCode(p1, p2, p3, p4):
    """Processes the section of the audio file that was loaded"""

def updateCodeBlock():
    userIn = codeBox.get("1.0", 'end-1c')
    codeFilePath = os.getcwd() + '/Assets/userCode.py'
    with open(codeFilePath, 'w') as userPy:
        userPy.write(userIn)
        userPy.close()

def createCustomCodeFile():
    codeFilePath = os.getcwd() + '/Assets/userCode.py'
    with open(codeFilePath, 'w') as userPy:
        userPy.write('def userCode(input, output, numChannels, numSamples, sampleRate, p1, p2, p3, p4):\n')
        userPy.write('    # You get an ndarray with a shape of {numChannels, numSamples} as an input\n\n')

        userPy.write('    # p1, p2, p3, p4 are the parameters set by the user.\n')
        userPy.write('    # if P1 is disabled then p1 = 0, so it would be nice to keep an eye on it\n\n')

        userPy.write('    # output is the ndarray that contains your processed data. Must be same shape as input\n')

        userPy.write('    output = input.copy()\n\n')
        userPy.write('    # Your code goes here....\n\n\n\n\n\n')
        userPy.write('    return output\n')

        userPy.close()

def updateCodeBox():
    codeFilePath = os.getcwd() + '/Assets/userCode.py'
    with open(codeFilePath, 'r') as userPy:
        data = userPy.read()
        codeBox.insert('1.0', data)
        userPy.close()

# ================= Plotting functions ======================

# Plot single waveform
def plotWaveform():
    global inputS
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
        g = np.zeros(len(inputS))

        # Quick fix to avoid division issues. Needs fixups <------
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
mainWindow = Tk()

# Main Window
mainWindow.geometry('1200x900')
mainWindow.title('DSP Visualiser')
mainWindow['background'] = '#680118'

# GUI
p1Frame = ParameterFrame(mainWindow, 1)
p1Frame.draw(240, 48, 40, 75)
p2Frame = ParameterFrame(mainWindow, 2)
p2Frame.draw(300, 48, 40, 75)
p3Frame = ParameterFrame(mainWindow, 3)
p3Frame.draw(360, 48, 40, 75)
p4Frame = ParameterFrame(mainWindow, 4)
p4Frame.draw(420, 48, 40, 75)

# File Chooser
chooseFileButton = Button(mainWindow, text='Choose File', command=chooseFile)
chooseFileButton.place(x=20, y=10, width=135, height=30)

# ================= File processing options ===============
startTime = tkinter.StringVar(mainWindow)
startTLabel = Label(mainWindow, text='Start', justify='center')
startTLabel.place(x=20, y=50, width=35, height=25)
startTBox = Entry(textvariable=startTime)
startTBox.place(x=60, y=50, width=45, height=25)

endTime = tkinter.StringVar(mainWindow)
endTLabel = Label(mainWindow, text='end', justify='center')
endTLabel.place(x=110, y=50, width=30, height=25)
endTBox = Entry(textvariable=endTime)
endTBox.place(x=145, y=50, width=45, height=25)

convertToMono = False
monoButton = Checkbutton(command=setMonoConversion)
monoButton.place(x=200, y=52, width=20, height=20)

# Process Part
processAudioButton = Button(mainWindow, text='Process Part', command=processAudio)
processAudioButton.place(x=20, y=80, width=150, height=25)

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
createCustomCodeFile()
updateCodeBox()

# ===============================================
# start App
mainWindow.mainloop()
# Recreate the file so upon next import there are no errors if user misspells sth
createCustomCodeFile()

