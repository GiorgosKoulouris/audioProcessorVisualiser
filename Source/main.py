import librosa as lr
import numpy as np
import matplotlib.pyplot as plt

# ================ Global Variables =====================

# ATM this is a const that points to a local audio file in my system
importPath = "/Users/cliff/Sirius/2.Projects/DOZEN/Stems/Vigil/Masters/Dozen_VIgil.wav"

sampleRate = 44100
inSignal = np.zeros(sampleRate)
durationInSecs = 3
outSignal = inSignal.copy

# =================== Function Definitions ============
# Import an audio file
def importFile():
    """Import the selected file"""
    global importPath
    global sampleRate
    global inSignal
    global durationInSecs
    global outSignal
    inSignal, sampleRate = lr.load(importPath, sr=None, offset=20, mono=True, duration=durationInSecs)
    outSignal = inSignal.copy

# You should copy your actual audio processing code in here
def processAudio(signal):
    """Processes the whole loaded audio file"""
    # Hard-clips the signal @ threshold and starts increasing when gain[x] > gain[x-1] (even if > threshold)

    # User Input
    thresholdInGain = .7
    release = 50

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
                    gain = out[sample] / inSignal[sample]
                    maxGainR = 1 - gain
                else:
                    out[sample] = -thresholdInGain
                    gain = out[sample] / inSignal[sample]
                    maxGainR = 1 - gain
        else:
            if (previousGain + (maxGainR * releaseDelta)) < 1:
                gain = previousGain + ((1 - previousGain) * releaseDelta)
            else:
                gain = 1

            out[sample] *= gain
            previousGain = gain
    return out

# Plot single waveform
def plotWaveform(signal, label):
    x = np.linspace(0, durationInSecs, len(inSignal))
    plt.plot(x, signal, color='b', label=label)
    plt.show()

# Plot both input and output
def plotStackedWaveforms():
    x = np.linspace(0, durationInSecs, len(inSignal))
    plt.plot(x, inSignal, color='g', label='Input')
    plt.plot(x, outSignal, color='b', label='Output')
    plt.show()

# Function that calculates gain reduction applied to the signal
def plotGain(alsoPlotWaveforms: bool):
    """This function plots the gain reduction over time"""
    """If <alsoPlotWaveforms = True>, it also plots a stacked overview of the waveforms"""
    g = outSignal / inSignal
    x = np.linspace(0, durationInSecs, len(inSignal))

    if alsoPlotWaveforms:
        fig, ax = plt.subplots(2, 1, sharex=True, num="Dynamics")
        ax[0].plot(x, g, color='r', label='Gain Reduction')
        ax[0].set_ylabel("Gain value")
        ax[1].plot(x, inSignal, color='g', label='y1')
        ax[1].plot(x, outSignal, color='b', label='y2')
        plt.xlabel("Time (s)")

    else:
        fig, ax = plt.subplots(1, 1, num="Dynamics")
        ax.plot(x, g, color='r', label='Gain Reduction')

    plt.xlabel("Time (s)")
    plt.ylabel("Sample Value")
    plt.legend()
    plt.show()


# ========= Execution ==========
importFile()
outSignal = processAudio(inSignal)
# plotWaveform(outSignal, "in")
# plotStackedWaveforms()
plotGain(False)
