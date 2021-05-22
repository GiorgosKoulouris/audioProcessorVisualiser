from tkinter import Frame, StringVar, Entry
from tkinter.ttk import Entry, Checkbutton, Label

class RenderRangeFrame:
    def __init__(self, parent):
        self.prnt = parent
        self.mFrame = Frame(self.prnt)

        self.mono = False

        self.startLabel = Label(self.mFrame, text='Start')
        self.startParam = StringVar(self.mFrame)
        self.startTextBox = Entry(self.mFrame, textvariable=self.startParam)

        self.endLabel = Label(self.mFrame, text='End')
        self.endParam = StringVar(self.mFrame)
        self.endTextBox = Entry(self.mFrame, textvariable=self.endParam)

        self.convertToMonoLabel = Label(self.mFrame, text='Mono')
        self.convertToMonoButton = Checkbutton(self.mFrame, command=self.setMono)

    def draw(self, x, y, w, h):
        self.mFrame.place(x=x, y=y, width=w, height=h)

        self.startLabel.place(x=0, y=0, width=.3*w, height=.5*h)
        self.endLabel.place(x=0, y=.5*h, width=.3*w, height=.5*h)
        self.startTextBox.place(x=.3*w, y=0, width=.3*w, height=.5*h)
        self.endTextBox.place(x=.3*w, y=.5*h, width=.3*w, height=.5*h)
        self.convertToMonoLabel.place(x=.6*w, y=0, width=.3*w, height=.5*h)
        self.convertToMonoButton.place(x=.7*w, y=.5*h, width=.15*w, height=.5*h)

    def getValues(self):
        # Apply strip only if textboxes contain sth to avoid exceptions
        if self.startTextBox.get() !=  "":
            s = int((self.startTextBox.get().strip()))
        else:
            s = 0
        if self.endTextBox.get() !=  "":
            e = int((self.endTextBox.get().strip()))
        else:
            e = 0
        return s, e, self.mono

    def setMono(self):
        if self.mono:
            self.mono = False
        else:
            self.mono = True

