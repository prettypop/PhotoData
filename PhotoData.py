#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import struct
from PIL import Image
from PIL.ExifTags import TAGS

Image.MAX_IMAGE_PIXELS = 1000000000 # このWarningを回避 [Image size (XXXXXXXX pixels) exceeds limit of 89478485 pixels, could be decompression bomb DOS attack.]

class Photo:
    
   def GetExif(self, img):
       
        exifKeys = [
            (271, "Make"),
            (272, "Model"),
            (274, "Orientation"),
            (305, "CreatorTool"),
            (36867, "DateTimeOriginal"),
            (33434, "ExposureTime"),
            (33437, "FNumber"),
            (34850, "ExposureProgram"),
            (34855, "ISOSpeedRatings"),
            (37377, "ShutterSpeedValue"),
            (37378, "ApertureValue"),
            (37379, "BrightnessValue"),
            (37380, "ExposureBiasValue"),
            (37381, "MaxApertureValue"),
            (37383, "MeteringMode"),
            (37384, "LightSource"),
            (37385, "Flash"),
            (37386, "FocalLength"),
            (41989, "FocalLengthIn35mmFilm"),
            (40961, "ColorSpace"), #SHORT
            (41990, "SceneCaptureType"),
            (41994, "Sharpness"),
            (41985, "CustomRendered"),
            (41986, "ExposureMode"),
            (41987, "WhiteBalance"),
            (42036, "LensModel"), # No NIKON lens data
            (50736, "LensInfo"), # Blank?
            (99999, "LensID"), # Blank?
            (37500, "MakerNote"),  # バイナリなので最後には""で上書き

        ]
        
        # Customized Exif Data list
        exifDataCust = {
            "Orientation_cust": "",
            "MeteringMode_cust": "",
            "WhiteBalance_cust": "",
            "LightSource_cust": "",
            "FNumber_cust": 0,
            "ExposureMode_cust": "",
            "ExposureTime_calc": 0,
            "ExposureTime_cust": "",
            "ExposureProgram_cust": "",
            "FocalLength_cust": 0,
            "CustomRendered_cust": "",
            "Sharpness_cust": "",
            "SceneCaptureType_cust": "",
            "ShutterSpeed_calc": 0,
            "ShutterSpeed_cust": "",
            "SubjectDistanceRange_cust": "",
            "ApertureValue_cust": 0,
            "BrightnessValue_cust": 0,
            "ExposureBiasValue_cust": 0,
            "MaxApertureValue_cust": 0,
        }
        
        # 数値データを変換
        exifOrientation = {
            "1" : "Horizontal (normal)",
            "2" : "Mirror horizontal",
            "3" : "Rotate 180",
            "4" : "Mirror vertical",
            "5" : "Mirror horizontal and rotate 270 CW",
            "6" : "Rotate 90 CW",
            "7" : "Mirror horizontal and rotate 90 CW",
            "8" : "Rotate 270 CW",
        }

        exifMeteringMode = {
            "0" : "Unknown",
            "1" : "Average",
            "2" : "CenterWeightedAverage",
            "3" : "Spot",
            "4" : "MultiSpot",
            "5" : "Pattern",
            "6" : "Partial",
            "255" : "other",
        }

        exifLightSource = {
            "0" : "Unknown",
            "1" : "Daylight",
            "2" : "Fluorescent",
            "3" : "Tungsten (incandescent light)",
            "4" : "Flash",
            "9" : "Fine weather",
            "10" : "Cloudy weather",
            "11" : "Shade",
            "12" : "Daylight fluorescent (D 5700 - 7100K)",
            "13" : "Day white fluorescent (N 4600 - 5400K)",
            "14" : "Cool white fluorescent (W 3900 - 4500K)",
            "15" : "White fluorescent (WW 3200 - 3700K)",
            "17" : "Standard light A",
            "18" : "Standard light B",
            "19" : "Standard light C",
            "20" : "D55",
            "21" : "D65",
            "22" : "D75",
            "23" : "D50",
            "24" : "ISO studio tungsten",
            "255" : "Other light source",
        }

        exifSharpness = {
            "0" : "Normal",
            "1" : "Soft",
            "2" : "Hard",
        }

        exifSubjectDistanceRange = {
            "0" : "Unknown",
            "1" : "Macro",
            "2" : "Close view",
            "3" : "Distant view",
        }
                    
        exifSceneCaptureType = {
            "0" : "Standard",
            "1" : "Landscape",
            "2" : "Portrait",
            "3" : "Night scene",
        }

        exifExposureProgram = {
            "0" : "Not defined",
            "1" : "Manual",
            "2" : "Normal program",
            "3" : "Aperture priority",
            "4" : "Shutter priority",
            "5" : "Creative program (biased toward depth of field)",
            "6" : "Action program (biased toward fast shutter speed)",
            "7" : "Portrait mode (for closeup photos with the background out of focus)",
            "8" : "Landscape mode (for landscape photos with the background in focus)",
        }

        exifCustomRendered = {
            "0" : "Normal process",
            "1" : "Custom process",
        }

        exifExposureMode = {
            "0" : "Auto exposure",
            "1" : "Manual exposure",
            "2" : "Auto bracket",
        }

        exifWhiteBalance = {
            "0" : "Auto white balance",
            "1" : "Manual white balance",
        }

        exifShutterSpeed1 = { # APEX値 ＝ - log2(露出時間)
                            "-5" : "30",
                            "-4" : "15",
                            "-3" : "8",
                            "-2" : "4",
                            "-1" : "2",
                            "0"  : "1",
                            "1"  : "1/2",
                            "2"  : "1/4",
                            "3"  : "1/8",
                            "4"  : "1/15",
                            "5"  : "1/30",
                            "6"  : "1/60",
                            "7"  : "1/125",
                            "8"  : "1/250",
                            "9"  : "1/500",
                            "10" : "1/1000",
                            "11" : "1/2000",
                            "12" : "1/4000", # 要確認
                            "13" : "1/8000", # 要確認
                            }

        exifShutterSpeed2 = { # APEX値 ＝ - log2(露出時間)
                            "-5" : 30,
                            "-4" : 15,
                            "-3" : 8,
                            "-2" : 4,
                            "-1" : 2,
                            "0"  : 1,
                            "1"  : 0.5,
                            "2"  : 0.25,
                            "3"  : 0.125,
                            "4"  : 0.067,
                            "5"  : 0.033,
                            "6"  : 0.017,
                            "7"  : 0.008,
                            "8"  : 0.004,
                            "9"  : 0.002,
                            "10" : 0.001,
                            "11" : 0.0005,
                            "12" : 0.00025, # 要確認
                            "13" : 0.000125, # 要確認
                        }

        exifApetureValue = { # APEX値 ＝ 2 log2(F値)
                            "0"  : 1,
                            "1"  : 1.4,
                            "2"  : 2,
                            "3"  : 2.8,
                            "4"  : 4,
                            "5"  : 5.6,
                            "6"  : 8,
                            "7"  : 11,
                            "8"  : 16,
                            "9"  : 22,
                            "10" : 32,
        }

        exifBrightnessValue = { # APEX値 ＝ log2(B / NK) Bはcd/cm2、N,Kは定数。
                            "-9" : "1/512", # 要確認
                            "-8" : "1/256", # 要確認
                            "-7" : "1/128", # 要確認
                            "-6" : "1/64", # 要確認
                            "-5" : "1/32", # 要確認
                            "-4" : "1/16", # 要確認
                            "-3" : "1/8", # 要確認
                            "-2" : "1/4",
                            "-1" : "1/2",
                            "0" : "1",
                            "1" : "2",
                            "2" : "4",
                            "3" : "8",
                            "4" : "15",
                            "5" : "30",
                            "6" : "60", # 要確認
                            "7" : "120", # 要確認
                            "8" : "240", # 要確認
                            "9" : "480", # 要確認
                            "10" : "960", # 要確認
                            "11" : "1920", # 要確認
                            "12" : "3840", # 要確認
                            "13" : "7680", # 要確認
        }


        exifData = {}
        makerNote = {}
        separator = "/"

        self.img = Image.open(img)
        self.exif = self.img._getexif()

        # 初期化
        for keys in exifKeys:
            exifData[keys[1]] = ""

        for keys in exifDataCust:
            exifData[keys] = ""

        # 個別に初期化が必要な項目の初期化
        for init in exifDataCust:
            exifData[init] = 0
            
        try:
            for id, val in self.exif.items():
                exifs = TAGS.get(id)
                
                # 全てのExif Dataをそのまま登録
                for keys in exifKeys:
                    if id == keys[0]:
                        exifData[keys[1]] = val
            
                # Maker Note分析
                """
                if exifs == "MakerNote":
                    makerNoteAll = exifData["MakerNote"]
                    print(type(makerNoteAll))
                    mmm = makerNoteAll.decode("UTF-8")
                    print(mmm)
                    mNote = str(makerNoteAll[0:8].encode("utf-8"))
                    print(mNote)

                    if mNote == "Nikon\x00\x01\x00":
                        makerNote["Maker"] = "Nikon"
                    if mNote == "FUJIFILM":
                        makerNote["Maker"] = "FUJIFILM"

                    print(makerNote)
                """
                exifData["MakerNote"] = ""
                
                round3 = lambda x:(x*2+1)//2 # Python3で0.5を繰り上げる四捨五入用lambda
                
                # 微調整の必要なExif Dataを設定
                if exifs == "DateTimeOriginal":
                    val = val.strip("\x00")
                elif exifs == "FocalLengthIn35mmFilm":
                    if val > 1000: # 一部機種 (SANYO DSC-MZ3など)で100倍の値が入っているのを調整
                        exifData["FocalLengthIn35mmFilm"] = val//100
                elif exifs == "FocalLength":
                    exifData["FocalLength_cust"] = int("{:.0f}".format(val[0] / val[1]))
                elif exifs == "ExposureTime":

                    if val[0] < val[1]:
                        if val[0] == 10:
                            if val[1] < 40: # 40は暫定的に設定
                                val2 = str("{:.1f}".format(val[0] / val[1]))
                            elif val[1] < 100: # 10/85 -> 1/9
                                #round3 = lambda x:(x*2+1)//2 # Python3で0.5を繰り上げる四捨五入用lambda
                                val2 = str("{:.0f}".format(val[0]/10)) + separator + str("{:.0f}".format(round3(val[1]/10)))
                            else: # 1/1600
                                val2 = str("{:.0f}".format(val[0]/10)) + separator + str("{:.0f}".format(val[1]/10))
                        else:
                            val2 = val[0]/val[1]
                            if val2%1 == 0:
                                val2 = str("{:.0f}".format(val2))
                            else:
                                val2 = str("{:.1f}".format(val2))
                    else:
                        val2 = val[0]/val[1]
                        if val2%1 == 0:
                            val2 = str("{:.0f}".format(val2))
                        else:
                            val2 = str("{:.1f}".format(val2))

                    exifData["ExposureTime_calc"] = float("{:.5f}".format(val[0] / val[1]))
                    exifData["ExposureTime_cust"] = val2
                elif exifs == "FNumber":
                    exifData["FNumber_cust"] = float("{:.1f}".format(val[0]/val[1]))

                elif exifs == "ShutterSpeedValue":
                    calc = str(int(round3(val[0]/val[1])))
                    if calc in exifShutterSpeed1:
                        #exifData["ShutterSpeed_cust"] = "[" + "{:02d}".format(int(calc) + 6) + "] " + exifShutterSpeed1[calc]
                        exifData["ShutterSpeed_cust"] = exifShutterSpeed1[calc]
                        exifData["ShutterSpeed_calc"] = exifShutterSpeed2[calc]
                    else:
                        # APEX値 ＝ - log2(露出時間)
                        calc=-val[0]/val[1]
                        realVal = str("{:.5f}".format(2**calc)) #+ " " + str(exifData["ShutterSpeed_cust"])

                        exifData["ShutterSpeed_cust"] = realVal
                        exifData["ShutterSpeed_calc"] = realVal

                elif exifs == "ApertureValue": 
                    calc = str(int(round3(val[0]/val[1])))
                    if calc in exifApetureValue:
                        exifData["ApertureValue_cust"] = exifApetureValue[calc]
                    else:
                        # APEX値 ＝ 2 log2(F値)
                        calc = (val[0]/val[1])/2
                        realVal = str("{:.1f}".format(2**calc)) #+ " " + str(exifData["ApertureValue_cust"])
                        exifData["ApertureValue_cust"] = realVal

                elif exifs == "MaxApertureValue":
                    calc = str(int(round3(val[0]/val[1])))
                    if calc in exifApetureValue:
                        exifData["MaxApertureValue_cust"] = exifApetureValue[calc]
                    else:
                        exifData["MaxApertureValue_cust"] = "No data: " + str(val)

                elif exifs == "BrightnessValue":
                    #    exifData["BrightnessValue_cust"] = int("{:.0f}".format(round3(val[0]/val[1])))
                    calc = str(int(round3(val[0]/val[1])))
                    if calc in exifBrightnessValue:
                        exifData["BrightnessValue_cust"] = "[" + "{:02d}".format(int(calc) + 10) + "] " + exifBrightnessValue[calc]
                    else:
                        exifData["BrightnessValue_cust"] = "Not calcurated"

                        # APEX値 ＝ log2(B / NK)
                
                elif exifs == "ExposureBiasValue":
                    exifData["ExposureBiasValue_cust"] = float("{:.1f}".format(val[0]/val[1]))

                elif exifs == "ISOSpeedRatings":
                    exifData["ISOSpeedRatings"] = val
                elif exifs == "Orientation":
                    if str(val) in exifOrientation:
                        exifData["Orientation_cust"] = exifOrientation[str(val)]
                elif exifs == "MeteringMode":
                    if str(val) in exifMeteringMode:
                        exifData["MeteringMode_cust"] = exifMeteringMode[str(val)]
                elif exifs == "LightSource":
                    if exifLightSource[str(val)] == "Unknown":
                        exifData["LightSource_cust"] = "Auto" # ManualAutoBalanceのAuto (Unknown)
                    elif val == "":
                        exifData["LightSource_cust"] = "Auto" # AutoWhiteBalanceのAuto (Blank)
                    else:
                        exifData["LightSource_cust"] = exifLightSource[str(val)]
                elif exifs == "Sharpness":
                    if str(val) in exifSharpness:
                        exifData["Sharpness_cust"] = exifSharpness[str(val)]
                elif exifs == "SubjectDistanceRange":
                    if str(val) in exifSubjectDistanceRange:
                        exifData["SubjectDistanceRange_cust"] = exifSubjectDistanceRange[str(val)]
                elif exifs == "SceneCaptureType":
                    if str(val) in exifSceneCaptureType:
                        exifData["SceneCaptureType_cust"] = exifSceneCaptureType[str(val)]
                elif exifs == "ExposureProgram":
                    if str(val) in exifExposureProgram:
                        exifData["ExposureProgram_cust"] = exifExposureProgram[str(val)]
                elif exifs == "CustomRendered":
                    if str(val) in exifCustomRendered:
                        exifData["CustomRendered_cust"] = exifCustomRendered[str(val)]
                elif exifs == "ExposureMode":
                    if str(val) in exifExposureMode:
                        exifData["ExposureMode_cust"] = exifExposureMode[str(val)]
                elif exifs == "WhiteBalance":
                    if str(val) in exifWhiteBalance:
                        exifData["WhiteBalance_cust"] = exifWhiteBalance[str(val)]
                elif exifs == "LensModel": # LensModelのバイナリデータ\x00を削除しないとファイル存在チェックでエラーになる。
                    temp = str(exifData["LensModel"])
                    temp = temp.split("\x00")
                    exifData["LensModel"] = temp[0]


        except AttributeError:
            return "[NO EXIF]"

        return exifData

