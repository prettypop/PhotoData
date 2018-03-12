#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import shutil
import ntpath
import subprocess
import re
import WriteLog
import PhotoData

class MoveRenamePhotoData:
    
    def FindAllFiles(self, directory):
        self.directory = directory
        for root, dirs, files in os.walk(self.directory):
            yield root
            for file in files:
                yield os.path.join(root, file)


    def MoveRename(self, fromDir, toDir, fileNameTemplate, dateTimeSeparator):

        self.fromDir = fromDir + "/"
        self.toDir = toDir + "/"

        exts = ("jpg", "png", "jpeg", "gif", "mov", "mp4", "heic")
        #extsNoExif = ("png", "gif", "mov", "mp4") # PNGとGIFにはEXIFは存在しない
        extsWithExif = ("jpg", "jpeg")

        writeLog = WriteLog.WriteLog()

        for file in self.FindAllFiles(self.fromDir):
            
            photoData = PhotoData.Photo()

            if os.path.dirname(file) != self.toDir[:-1]: # fromDirとtoDirが同じ場合、同じ場所にあるファリは無視
                root, ext = os.path.splitext(file)

                if ext[1:].lower() in exts:

                    # - - - - - - - - - -
                    # get created date
                    # - - - - - - - - - -
                    try: # 2018.01.25 Error対応
                        creTime = time.localtime(os.stat(file).st_birthtime) # File作成日
                        creYYYYMMDD = str(creTime[0]) + str(creTime[1]).rjust(2,'0')  + str(creTime[2]).rjust(2,'0')
                        creYYYYMMDD_HHMMSS = creYYYYMMDD + " " + str(creTime[3]).rjust(2,'0') + str(creTime[4]).rjust(2,'0') + str(creTime[5]).rjust(2,'0')
                        taginfo = ""
                    except FileNotFoundError as err: # 2018.01.25 Error対応
                        writeLog.WriteLog("* EXCEPTION (FileNotFoundError): " + str(err))
                        taginfo = "[RETRY]"
                    except OverflowError as err: # 2018.01.25追加
                        writeLog.WriteLog("* EXCEPTION (FileNotFoundError): " + str(err))
                        taginfo = "[RETRY]"

                    if taginfo == "[RETRY]":
                        writeLog.WriteLog(": [" + file + "]")
                        creYYYYMMDD = "00000000"
                        creYYYYMMDD_HHMMSS = "00000000 000000"
                        writeLog.WriteLog("* RETRY LATER...")
                    else: pass

                    if taginfo == "":
                        # - - - - - - - - - -
                        # toDir存在Check & create if not available
                        # - - - - - - - - - -
                        toDirSub = self.toDir + creYYYYMMDD
                        if os.path.exists(toDirSub) == False:
                            os.mkdir(toDirSub)
                        else: pass


                        # - - - - - - - - - -
                        # Convert HEIC file to JPEG
                        # - - - - - - - - - -
                        if ext[1:].lower() == "heic":
                            # - - - - - - - - - -
                            # Convert from HEIC to JPEG using sips command
                            # - - - - - - - - - -
                            file_heic = file
                            file_jpeg = file.replace(".heic", ".jpg")
                            res = subprocess.run(["sips", "--setProperty", "format", "jpeg", file_heic, "--out", file_jpeg], stdout=subprocess.PIPE)

                            if res.returncode == 0:
                                writeLog.WriteLog("> File conversion from HEIC to JPEG: COMPLETED [StdErr:" + str(res.stderr) + "]")
                                writeLog.WriteLog("| form [" + file_heic + "]")
                                writeLog.WriteLog("| to   [" + file_jpeg + "]")
                                os.remove(file_heic)
                                file = file_jpeg
                                _, ext = os.path.splitext(file)
                            else:
                                writeLog.WriteLog("> File conversion from HEIC to JPEG: !!!FAILED!!! [StdErr:" + str(res.stderr) + "]")
                                writeLog.WriteLog("| StdOut: " + str(res.stdout))
                                taginfo = "[RETRY]"

                        else: pass

                                          
                        # - - - - - - - - - -
                        # EXIF Dataを取得し、でRenameのtoNameを設定
                        # - - - - - - - - - -
                        if ext[1:].lower() in extsWithExif:
                            try:
                                taginfo = photoData.GetExif(file)
                            except OSError as err: # 2018.01.08 Error対応
                                writeLog.WriteLog("* EXCEPTION (OSError): " + str(err))
                                writeLog.WriteLog(": [" + file + "]")
                                taginfo = "[RETRY]"
                                #writeLog.WriteLog("* RETRY LATER...")
                        else:
                            taginfo = "[NO EXIF]"
                    else: pass

                    # - - - - - - - - - -
                    # Rename with EXIF
                    # - - - - - - - - - -
                    if taginfo != "[NO EXIF]" and taginfo != "[RETRY]":
                        root, ext = os.path.splitext(file)
                        
                        if str(taginfo["DateTimeOriginal"]) == "":
                            toName = creYYYYMMDD_HHMMSS + ext
                        else:
                            # - - - - - - - - - -
                            # Rename by tagName
                            # - - - - - - - - - -
                            toName = fileNameTemplate + ext
                            for tagName in taginfo:
                                replaceWord = str(taginfo[tagName])
                                if tagName == "DateTimeOriginal":
                                    replaceWord = replaceWord[0:19]
                                else: pass

                                toName = toName.replace("$" + tagName + "$", replaceWord)

                            if dateTimeSeparator.lower() == "none":
                                toName = toName.replace(":", "")
                            else:
                                toName = toName.replace(":", dateTimeSeparator)

                        toName = toName.replace("  ", " ") # 二重スペースを圧縮

                        fpath, fname = ntpath.split(file)
                        fromNameFull = file

                        # Pythonでファイル名に使用できない文字(\　/　:　?　"　<　>　\　|)を"_"に変換 plus [,]も変換(影響なければ削除予定)
                        fname, ext = os.path.splitext(toName) # file nameとextensionを分離
                        toNameFull = fpath + "/" + re.sub(r'[\\|/|:|?|.|"|<|>|\|]|,', '_', fname) + ext

                        #print("["+fromNameFull+"]")
                        #print("["+toNameFull+"]")

                        os.rename(fromNameFull, toNameFull)
                        writeLog.WriteLog("> Rename file (with EXIF): COMPLETED")
                        writeLog.WriteLog("| from [" + file + "]")
                        writeLog.WriteLog("| to   [" + toNameFull + "]")
                        
                        fromNameFull = toNameFull # SuffixのRenameの際にEXIFでRenameしたFileをfromNameFullにする。

                    elif taginfo == "[NO EXIF]":
                        fromNameFull = file
                        toNameFull = file
                    else: pass


                    # - - - - - - - - - -
                    # Move file and remove subfolder
                    # - - - - - - - - - -
                    if taginfo != "[RETRY]":

                        # - - - - - - - - - -
                        # (1) 重複ファイルにSuffix追加
                        # - - - - - - - - - -
                        # - - - - - - - - - -
                        # 重複ファイルにSuffix追加
                        # 重複確認はファイルの移動先にすでに存在しているかどうかで確認
                        # Suffixは2枚目の重複ファイルから付与するので、最初のファイルには付与されない
                        # - - - - - - - - - -
                        fn_to, ext_to = os.path.splitext(os.path.basename(toNameFull))
                        destNameFull = toDirSub + "/" + fn_to + ext_to
                        
                        fpath, fname = ntpath.split(toNameFull)
                        
                        suf = 0
                        sufs = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z") # 連射は1分間に数枚なのでzまでは不要だと思うが...

                        while True:
                            if os.path.exists(destNameFull):
                                suf += 1
                                    
                                fn_ext = fn_to + sufs[suf - 1] + ext_to
                                toNameFull = fpath + "/" + fn_ext
                                destNameFull = toDirSub + "/" + fn_ext
                            else: break

                        if suf != 0:
                            os.rename(fromNameFull, toNameFull)
                            writeLog.WriteLog("> Rename file (add suffix): COMPLETED")
                            writeLog.WriteLog("| from [" + fromNameFull + "]")
                            writeLog.WriteLog("| to   [" + toNameFull + "]")
                        else: pass


                        # - - - - - - - - - -
                        # (2) Move file
                        # - - - - - - - - - -
                        fpath, fname = ntpath.split(toNameFull)
                        try: # 2018.01.25 Error対応
                            shutil.move(toNameFull, toDirSub)
                            writeLog.WriteLog("> Move file: COMPLETED")
                            writeLog.WriteLog("| from [" + toNameFull + "]")
                            writeLog.WriteLog("| to   [" + toDirSub + "/" + fname + "]")
                        except shutil.Error as err:
                            writeLog.WriteLog("* EXCEPTION (shutil.Error): " + str(err))
                            writeLog.WriteLog(": [" + toNameFull + "]")
                            taginfo = "[RETRY]"


                        # - - - - - - - - - -
                        # (3) Subfolder削除
                        # - - - - - - - - - -
                        if os.path.dirname(file) != self.fromDir[:-1]: # fromDirの場合、rmdirしない
                            try:
                                os.rmdir(os.path.dirname(file))
                            except:
                                pass
                        else: pass

                        if os.path.exists(os.path.dirname(file)) == False:
                            writeLog.WriteLog("> Delete folder: COMPLETED")
                            writeLog.WriteLog("| [" + os.path.dirname(file) + "]")
                        else: pass

                    else: pass

                    if taginfo == "[RETRY]":
                        writeLog.WriteLog("* RETRY LATER...")
                    else: pass

                    writeLog.WriteLog("--")
                else: pass
