from tkinter import Tk, Menubutton, Menu, Frame, StringVar
from tkinter.ttk import Entry

class ParameterFrame:
    parent = Tk
    paramNumber = 1

    def __init__(self, mainWin: Tk, parNumber: int):
        self.parent = mainWin
        self.paramNumber = parNumber
        self.choice = 0

        self.myFrame = Frame(self.parent)
        self.param = StringVar(self.myFrame)
        self.textBox = Entry(self.myFrame, textvariable=self.param)
        if self.paramNumber == 1:
            self.menuButton = Menubutton(self.myFrame, text='P1', activebackground='blue')
        elif self.paramNumber == 2:
            self.menuButton = Menubutton(self.myFrame, text='P2', activebackground='blue')
        elif self.paramNumber == 3:
            self.menuButton = Menubutton(self.myFrame, text='P3', activebackground='blue')
        elif self.paramNumber == 4:
            self.menuButton = Menubutton(self.myFrame, text='P4', activebackground='blue')

        self.menuButton.pack()
        self.textBox.pack()

        self.menuButton.menu = Menu(self.menuButton, tearoff=0)
        self.menuButton["menu"] = self.menuButton.menu
        self.pMenu = Menu(self.menuButton, tearoff=0)
        self.pMenu.add_command(label='disabled', command=self.setChoice0)
        self.pMenu.add_command(label='int', command=self.setChoice1)
        self.pMenu.add_command(label='float', command=self.setChoice2)

        self.menuButton.config(menu=self.pMenu)

    def draw(self, xIn, yIn, wIn, hIn):
        self.myFrame.place(x=xIn, y=yIn, width=wIn, height=hIn)

    def getValue(self):
        p = self.param.get()
        if self.choice == 1:
            return int(p.strip())
        elif self.choice == 2:
            return float(p.strip())

    def setChoice0(self):
        self.choice = 0

    def setChoice1(self):
        self.choice = 1

    def setChoice2(self):
        self.choice = 2
