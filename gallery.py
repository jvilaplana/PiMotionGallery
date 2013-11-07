#!/usr/bin/env python

import logging # http://docs.python.org/2/howto/logging.html#logging-basic-tutorial
import Image
import ImageTk
import Tkinter as tk
import os
from Tkinter import *
from time import sleep

class Gallery(tk.Frame):
    def __init__(self, pmg, master=None):
        tk.Frame.__init__(self, master)

        ## Canvas
        self.cnv = Canvas(self)
        self.cnv.grid(row=3, column=0, sticky='nswe')
        ## Scrollbars for canvas
        self.hScroll = Scrollbar(self, orient=HORIZONTAL, command=self.cnv.xview)
        self.hScroll.grid(row=4, column=0, sticky='we')
        self.vScroll = Scrollbar(self, orient=VERTICAL, command=self.cnv.yview)
        self.vScroll.grid(row=3, column=1, sticky='ns')
        self.cnv.configure(xscrollcommand=self.hScroll.set, yscrollcommand=self.vScroll.set)
        ## Frame in canvas
        self.frm = Frame(self.cnv)
        ## This puts the frame in the canvas's scrollable zone
        self.cnv.create_window(0, 0, window=self.frm, anchor='nw')
        ## Frame contents
        ## Update display to get correct dimensions
        self.frm.update_idletasks()
        ## Configure size of canvas's scrollable zone
        self.cnv.configure(scrollregion=(0, 0, self.frm.winfo_width(), self.frm.winfo_height()))



        self.pmg = pmg
        self.parent = master
        self.dirButtons = []
        self.currentDir = None
        self.images = []
        self.currentImage = 0
        self.imageLabel = None
        self.activeStat = tk.BooleanVar(self)
        self.activeStat.set(True)
        self.playSpeed = 80

        self.initialize()
        self.createWidgets()
        self.createMenu()

        self.update()
        self.grid()
        self.showDirectories()

    def initialize(self):
        pass


    def fetchImages(self):
        self.pmg.fetchImages()
        print "Fetching images ..."

    def createWidgets(self):
        #self.entry = tk.Entry(self)
        #self.entry.grid(column=0, row=0, sticky='EW')

        label = tk.Label(self, text="PiMotionGallery v0.1", fg="white",bg="blue")
        label.grid(column=0,row=0,columnspan=10,sticky='EW')

        self.grid_columnconfigure(0,weight=1)

        button = tk.Button(self,text=u"Fetch images", command=self.fetchImages)
        button.grid(column=0,row=1)

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(column=1,row=1)

        nextButton = tk.Button(self,text="Next", command=self.nextImg)
        nextButton.grid(column=2,row=1)

        playButton = tk.Button(self,text="Play", command=self.play)
        playButton.grid(column=3,row=1)

        playButton = tk.Button(self,text="Stop", command=self._stop)
        playButton.grid(column=4,row=1)

        slider = Scale(self, from_=0, to=100, orient=HORIZONTAL, command=self._playSpeed)
        slider.set(self.playSpeed)
        slider.grid(column=1,row=2)

        photo = ImageTk.PhotoImage(ImageTk.Image.open('default.jpg'))
        self.imageLabel = tk.Label(self, border=25)
        self.imageLabel['text'] = 'wololo'
        self.imageLabel['image'] = photo
        self.imageLabel.photo = photo
        self.imageLabel.grid(row=1, column=5, columnspan=5, rowspan=30, sticky=W+E+N+S, padx=5, pady=5)

    # Creates the application menu
    def createMenu(self):
        # Create a toplevel menu
        menubar = Menu(self.master)

        # File pulldown menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Quittt", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Help pulldown menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.quit)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # Display the menu
        self.master.config(menu=menubar)

    def showDirectories(self):
        local = self.pmg.config['motion_local']
        i = 1
        for root, dirs, files in os.walk(local):
            dirbutton = Button(self.frm, text=root, command=lambda root=root: self.selectDir(root))
            #self.dirButtons.append(dirbutton)
            #dirbutton.grid(column=0, row=1+i)
            dirbutton.pack(side=TOP, padx=2, pady=2)
            i = i + 1
        self.frm.update_idletasks()
        ## Configure size of canvas's scrollable zone
        self.cnv.configure(scrollregion=(0, 0, self.frm.winfo_width(), self.frm.winfo_height()+20))

    def selectDir(self, dir):
        files = [f for f in os.listdir(dir + '/') if ".jpg" in f]
        self.currentDir = dir
        self.currentImage = 0
        self.images = files
        photo = ImageTk.PhotoImage(ImageTk.Image.open(self.currentDir + '/' + self.images[self.currentImage]))
        label = Label()
        label['text'] = self.images[self.currentImage]
        label['image'] = photo
        label.photo = photo
        self.imageLabel.config(image=photo)
        self.update()

    def nextImg(self):
        if len(self.images) > self.currentImage + 1:
            self.currentImage = self.currentImage + 1
            try:
                photo = ImageTk.PhotoImage(ImageTk.Image.open(self.currentDir + '/' + self.images[self.currentImage]))
                label = Label()
                label['text'] = self.images[self.currentImage]
                label['image'] = photo
                label.photo = photo
                self.imageLabel.config(image=photo)
            except:
                print "ERROR [nextImg]"

    def play(self):
        for i in self.images:
            if self.activeStat.get():
                self.nextImg()
                sleep(self.playSpeed)
                self.update()
            else:
                self.activeStat.set(True)
                break

    def _playSpeed(self, value):
        self.playSpeed = (1000 - int(value) * 10) / 1000

    def _stop(self):
        self.activeStat.set(False)
