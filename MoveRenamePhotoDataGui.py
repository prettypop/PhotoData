#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import tkinter
import time
import MoveRenamePhotoData
import WriteLog


# Button 1
def ExitWindow(self):
    root.quit()


# Loop
def Loop():
    moveRenamePhotoData = MoveRenamePhotoData.MoveRenamePhotoData()

    for dirFrom, dirTo in dirFromTo:
        moveRenamePhotoData.MoveRename(dirFrom, dirTo, fileNameTemplate, dateTimeSeparator)
    root.after(timeInterval, Loop) # timeInterval(ms)毎にLoop()を呼び出す


# - - - - - - - - - - -
# Start from...
# - - - - - - - - - - -
dirFromTo = []

timeInterval=1000 #ms
param = "None"

writeLog = WriteLog.WriteLog()

# print("> load ini file")
for line in open('MoveRenamePhotoData.ini', 'r'):
    line = line.strip()
    if line == "": pass
    elif line[0:1] == "#": pass
    else:
        item, param =  line.split("=", 1)
            
        if item == "MoveFromTo":
            dirFrom, dirTo = param.split(",")
            dirFrom = dirFrom.strip()
            dirTo = dirTo.strip()
            dirFromTo.append([dirFrom, dirTo])
        if item == "DateTimeSeparator":
            dateTimeSeparator = param
        if item == "FileNameTemplate":
            fileNameTemplate = param
        if item == "TimeInterval":
            if param == "":
                param = "None"
            timeInterval = param


#
# GUI Setting
#
root = tkinter.Tk()

root.title(u"Move Photo Data")
root.geometry("400x300")

#ボタン
Button = tkinter.Button(text=u'Exit', width=50)
Button.bind("<Button-1>", ExitWindow)
Button.pack()
#
# End of GUI Setting
#


# print("> Start...")

writeLog.WriteLog("* * * * * MoveRenamePhotoData * * * * *")

Loop()


root.mainloop()
