"""
================================== USAGE ===============================

Intended Usage (with implemented functionality):
    1. Choose start and end times (in secs) and click import to load the file
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

# =================== Function Definitions ============
# Import an audio file
def importFile():
    """Import the selected file"""
    rangeIsCorrect = ((int(startTime.get())) >= 0) and ((int(endTime.get()) > int(startTime.get())))
    if rangeIsCorrect:
        tempPath = askopenfilename()
        if tempPath.endswith(".wav"):
            global importPath
            global sampleRate
            global inputS
            global durationInSecs
            global output

            importPath = tempPath

            durationInSecs = int(endTime.get()) - int(startTime.get())
            inputS, sampleRate = lr.load(importPath, sr=None, offset=20, mono=True, duration=durationInSecs)
            output = processAudio(inputS)

            global fileImported
            fileImported = True

# User will actually override this function
def processAudio(signal):
    """Processes the section of the audio file that was loaded"""
    # Sample code, for demonstration purposes

    """
    Hard-clips the signal @ threshold and starts increasing  gain when 
    gain[x] > gain[x-1] (even if > threshold)
    """

    # User inputS
    thresholdInGain = .7
    release = 250

    # Calculations
    releaseDelta = 1 / ((release / 1000) * sampleRate)
    maxGainR = 0
    previousGain = 1
    out = signal.copy()
    gain = 1
    for sample in range(len(out)):
        if abs(out[sample]) >= thresholdInGain:
            tempGain2 = thresholdInGain / abs(out[sample])
            if tempGain2 > previousGain:
                gain = previousGain + ((tempGain2 - previousGain) * releaseDelta)
                out[sample] *= gain
                maxGainR = 1 - gain
            else:
                if out[sample] > 0:
                    out[sample] = thresholdInGain
                    gain = out[sample] / inputS[sample]
                    maxGainR = 1 - gain
                else:
                    out[sample] = -thresholdInGain
                    gain = out[sample] / inputS[sample]
                    maxGainR = 1 - gain
        else:
            if (previousGain + (maxGainR * releaseDelta)) < 1:
                gain = previousGain + ((1 - previousGain) * releaseDelta)
            else:
                gain = 1

            out[sample] *= gain
            previousGain = gain
    return out

# ================= Plotting functions ======================

# Plot single waveform
def plotWaveform(signal, label):
    x = np.linspace(0, durationInSecs, len(inputS))
    fig, ax = plt.subplots(1, 1, num="Single Waveform")
    ax.plot(x, signal, color='g', label=label)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Sample value")
    fig.show()

# Plot both inputS and output
def plotStackedWaveforms():
    x = np.linspace(0, durationInSecs, len(inputS))
    fig, ax = plt.subplots(1, 1, num="Stacked Waveforms")
    ax.plot(x, inputS, color='g', label='inputS')
    ax.plot(x, output, color='b', label='Output')

    fig.show()

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

        else:
            fig, ax = plt.subplots(1, 1, num="Gain Over Time")
            ax.plot(x, g, color='r', label='Gain')
            plt.xlabel("Time (s)")
            plt.ylabel("Gain Value")

        plt.legend()
        plt.show()

# This function initialises all GUI elements
def initUI(window: Tk):
    window.geometry('600x600')
    window.title('DSP Visualiser')

    global startTime
    startTime = tkinter.StringVar(window)
    startTLabel = Label(window, text='start', justify='center')
    startTLabel.place(x=10, y=10, width=40, height=30)
    startTBox = Entry(textvariable=startTime)
    startTBox.place(x=55, y=10, width=35, height=30)

    global endTime
    endTime = tkinter.StringVar(window)
    endTLabel = Label(window, text='end', justify='center')
    endTLabel.place(x=100, y=10, width=30, height=30)
    endTBox = Entry(textvariable=endTime)
    endTBox.place(x=135, y=10, width=35, height=30)

    importFileButton = Button(window, text='Import', command=importFile)
    importFileButton.place(x=500, y=10, width=75, height=30)

    global includeWavesInGainPlot
    includeWavesInGainPlot = False
    wavesInGainButton = Checkbutton(variable=includeWavesInGainPlot, command=setIncludeWavesInGain)
    wavesInGainButton.place(x=50, y=50, width=35, height=35)

    plotGainButton = Button(window, text='Plot gain over time', command=plotGain)
    plotGainButton.place(x=120, y=50, width=200, height=35)


# ========== App loop =============
mainWindow = Tk()
initUI(mainWindow)

mainWindow.mainloop()

