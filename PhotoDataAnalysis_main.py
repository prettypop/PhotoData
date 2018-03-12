import os
import ntpath
import datetime
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import re
import PhotoData

def FindAllFiles(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)


def GetExifData(lists, ignoreCameraModel, fileFullPath):

    photoData = PhotoData.Photo()

    exts = ("jpg", "jpeg")
    list = []
    header = []

    i = 0

    print("[" + fileFullPath + "]")

    for file in FindAllFiles(fileFullPath):

        root, ext = os.path.splitext(file)
        if ext[1:].lower() in exts:
            try:
                taginfo = photoData.GetExif(file)

                fpath, fname = ntpath.split(file)
                root, ext = os.path.splitext(file)

                loadData = False

                if taginfo != "[NO EXIF]" and str(taginfo["Model"]) != "":
                    if ignoreCameraModel == []:                 loadData = True
                    elif taginfo["Model"] in ignoreCameraModel: loadData = False
                    else:                                       loadData = True

                    if loadData == True:
                        i += 1

                        if i == 1:
                            n = 0
                            for value in taginfo.keys():
                                n += 1
                                if n == 1: header.append("FileName")
                                else: pass
                                header.append(value)
                        else: pass

                        n = 0
                        for value in taginfo.values():
                            n += 1
                            if n == 1: list.append(fname)
                            else: pass
                            
                            list.append(value)

                        lists.append(list)
                        list = []
                    else: pass
                else: pass

            except AttributeError as err:
                print("*EXCEPTION:", err)
                print(" [" + file + "]")
        else: pass

    return(lists, header)

#
# 日付関連データの取得
#
def GetYear(dateTime):
    dateTime = str(CheckDate(dateTime))
    return(int(dateTime[0:4]))

def GetMonth(dateTime):
    month = {
            "01":"[01]Jan",
            "02":"[02]Feb",
            "03":"[03]Mar",
            "04":"[04]Apr",
            "05":"[05]May",
            "06":"[06]Jun",
            "07":"[07]Jul",
            "08":"[08]Aug",
            "09":"[09]Sep",
            "10":"[10]Oct",
            "11":"[11]Nov",
            "12":"[12]Dec"
            }

    dateTime = str(CheckDate(dateTime))
    return(month[dateTime[5:7]])

def GetYearMonth(dateTime):
    dateTime = str(CheckDate(dateTime))
    return(dateTime[0:7].replace(":", "/"))

def GetHour(dateTime):
    dateTime = str(CheckDate(dateTime))
    return(int(dateTime[11:13]))

def GetWeek(dateTime):
    week = (
            "[0]Monday",
            "[1]Tuesday",
            "[2]Wednesday",
            "[3]Thursday",
            "[4]Friday",
            "[5]Saturday",
            "[6]Sunday"
            )
    dateTime = CheckDate(dateTime)
    retWeek = week[dateTime.weekday()]
    return(retWeek)

def CheckDate(dateTime):
    
    month = {
            "Jan":"01",
            "Feb":"02",
            "Mar":"03",
            "Apr":"04",
            "May":"05",
            "Jun":"06",
            "Jul":"07",
            "Aug":"08",
            "Sep":"09",
            "Oct":"10",
            "Nov":"11",
            "Dec":"12"
            }
    
    dateTime = dateTime.replace("-", ":")
    # "    :  :     :  :  " or "0000:00:00 00:00:00"
    if dateTime == "    :  :     :  :  ": dateTime = "1968:01:01 00:00:00"
    if dateTime == "0000:00:00 00:00:00": dateTime = "1968:01:01 00:00:00"
    if len(dateTime) == 0: dateTime = "1900:01:01 00:00:00"

    # DateTimeがこのType: 19 Mar 2008 14:02:20
    if len(dateTime) > 0 and dateTime[2:3] == " ":
        YYYY = dateTime[7:11]
        MM = month[dateTime[3:6]]
        DD = dateTime[0:2]
        HH = dateTime[12:14]
        dateTime = str(YYYY) +":" + str(MM) + ":" + str(DD) + " " + str(HH) + ":00:00"
    
    dateTime = dateTime[0:19]
    try:
        dateTime = datetime.datetime.strptime(dateTime, '%Y:%m:%d %H:%M:%S')
    except:
        print("*ERROR?:" + dateTime)
    
    return(dateTime)


def ModifyName(name):
    if name[-5:] == "_cust": name = name[0:-5]
    if name[-5:] == "_calc": name = name[0:-5]
    return(name)

# 長い名称を縮小
def ReduceName(fn):
    fn = fn.replace("FocalLengthIn35mmFilm", "FLen35mm")
    fn = fn.replace("FocalLength", "FLen")
    fn = fn.replace("LensModel", "Lens")
    fn = fn.replace("ISOSpeedRatings", "ISOSpeed")

    fn = fn.replace("ApertureValue", "Aperture")
    fn = fn.replace("BrightnessValue", "Brightness")
    fn = fn.replace("ExposureBiasValue", "ExposureBias")
    fn = fn.replace("MaxApertureValue", "MaxAperture")
    fn = fn.replace("SceneCaptureType", "SceneCapture")
    
    fn = fn.replace("Year_Month", "Year_MM")
    fn = fn.replace(" & ", "_")
    return(fn)

#
# pythonでデータ書き出しの際に「openpyxl.utils.exceptions.IllegalCharacterError」が出たときの対応
# "import re"が必要
#
def illegal_char_remover(data):
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]|[\x00-\x1f\x7f-\x9f]|[\uffff]')
    
    # Remove ILLEGAL CHARACTER.
    if isinstance(data, str):
        return ILLEGAL_CHARACTERS_RE.sub("", data)
    else:
        return data


def main():
    
    photoData = PhotoData.Photo()
    
    lists = []
    header = []
    cols = []

    # Set initial data
    photoDirectories =[]
    ignoreCameraModel =[]
    fillEmptyLensModel = { "DSC-RX100M3": "No Lens Data",} # sample
    PlotBarRotate = {}

    # Set plot initial data
    plotFixSizeX = 12
    plotFixSizeY = 8
    plotGrid = False
    plotSubPlots = False
    plotFontSize = 10
    plotRotate = 0
    
    plotBar = False
    plotScatter = False
    plotHexbin = False
    plotPie = False

    for line in open('PhotoDataAnalysis.ini', 'r'):
        line = line.strip()
        if line == "":
            pass
        elif line[0:1] == "#":
            pass
        else:
            item, param =  line.split("=", 1)
            if item == "PhotoDirectory"     : photoDirectories.append(param)
            if item == "IgnoreCameraModel"  : ignoreCameraModel.append(param)
            if item == "FillEmptyLensModel":
                param1, param2 = param.split(":", 1)
                fillEmptyLensModel[param1] = param2.strip()
            if item == "PlotFigSizeX"       : plotFixSizeX = int(param)
            if item == "PlotFigSizeY"       : plotFixSizeY = int(param)
            if item == "PlotGrid":
                if param.lower() == "true"  : plotGrid = True
                else                        : plotGrid = False
            if item == "PlotSubPlots":
                if param.lower() == "true"  : plotSubPlots = True
                else                        : plotSubPlots = False
            if item == "PlotsFontSize"      : plotFontSize = param # Default値
            if item == "PlotBarRotate":
                param1, param2 = param.split(":")
                PlotBarRotate[param1] = int(param2)
                if param1 == "Default"      : plotRotate = param2
            if item == "PlotBar":
                if param == "True"          : plotBar = True
                else                        : plotBar = False
            if item == "PlotScatter":
                if param == "True"          : plotScatter = True
                else                        : PlotScatter = False
            if item == "PlotHexbin":
                if param == "True"          : plotHexbin = True
                else                        : plotHexbin = False
            if item == "PlotPie":
                if param == "True"          : plotPie = True
                else                        : plotPie = False
            if item == "PlotSeaborn":
                if param == "True"          : plotSeaborn = True
                else                        : plotSeaborn = False



    print("#")
    print("#")
    print("#")
    print("# Load and analyze photo data")
    print("#")
    print("#")
    print("#")

    print("> Load photo data")
    for photoDirectory in photoDirectories:
        lists, header = GetExifData(lists=lists, ignoreCameraModel=ignoreCameraModel, fileFullPath=photoDirectory)
        if header != []: cols = header

    now = datetime.datetime.now()
    now_dt = str(now.year).zfill(2) + str(now.month).zfill(2) + str(now.day).zfill(2) + " " + str(now.hour).zfill(2) + str(now.minute).zfill(2) + str(now.second).zfill(2)

    # Data保存先ディレクトリ
    if os.path.exists("./Data") == False: os.mkdir("./Data")

    dataDir = "./Data/" + now_dt
    os.mkdir(dataDir)

    #
    # このエラーが出た時の確認用: AssertionError: 45 columns passed, passed data had 43 columns
    #
    #for x in lists:
    #    print(str(len(x)) + ":" + x[0] )


    # - - -
    # Set PANDAS
    # - - -
    df = pd.DataFrame(data=lists, columns=cols)
    df = df.applymap(illegal_char_remover)

    df["Count"] = df.apply(lambda x: 1, axis=1)

    #iPhoneのMakeがBlankの時に更新
    df["Make"] = df.apply(lambda x: "Apple" if x.Model[0:6] == "iPhone" else x.Make, axis=1)

    #LensModelがEmptyの時に更新
    df["LensModel_org"] = df.apply(lambda x: x.LensModel, axis=1) # Backup
    df["LensModel"] = df.apply(lambda x: "Unknown" if x.LensModel == "" else x.LensModel, axis=1)
    df["LensModel"] = df.apply(lambda x: fillEmptyLensModel[x.Model] if x.Model in fillEmptyLensModel and x.LensModel == "Unknown" else x.LensModel, axis=1)

    # EXIF Dataの数値がブランクのものを0で埋める
    df["ISOSpeedRatings"] = df.apply(lambda x: 0 if x.ISOSpeedRatings == "" else x.ISOSpeedRatings , axis=1)
    df["FNumber_cust"] = df.apply(lambda x: 0 if x.FNumber_cust == "" else x.FNumber_cust , axis=1)
    df["ExposureTime_calc"] = df.apply(lambda x: 0 if x.ExposureTime_calc == "" else x.ExposureTime_calc , axis=1)
    df["ExposureTime_cust"] = df.apply(lambda x: 0 if x.ExposureTime_cust == "" else x.ExposureTime_cust , axis=1)
    df["FocalLengthIn35mmFilm"] = df.apply(lambda x: 0 if x.FocalLengthIn35mmFilm == "" else x.FocalLengthIn35mmFilm , axis=1)

    df["LightSource_cust"] = df.apply(lambda x: "Auto" if x.LightSource_cust == 0 else x.LightSource_cust , axis=1)

 
    # 年。月、曜日、時間帯の列を追加
    df["Year"]       = df.apply(lambda x: GetYear(x.DateTimeOriginal),      axis=1)
    df["Month"]      = df.apply(lambda x: GetMonth(x.DateTimeOriginal),     axis=1)
    df["Year_Month"] = df.apply(lambda x: GetYearMonth(x.DateTimeOriginal), axis=1)
    df["Hour"]       = df.apply(lambda x: GetHour(x.DateTimeOriginal),      axis=1)
    df["Week"]       = df.apply(lambda x: GetWeek(x.DateTimeOriginal),      axis=1)

    # List Camera Model
    print("[Camera Model List]")
    pvt_cm = pd.pivot_table(df, values="Count", index=["Make", "Model"], aggfunc=lambda x: len(x))
    print(pvt_cm)


    # - - -
    # Create charts
    # - - -
    print("[Create Charts]")

    # Sort of bar chart
    plots_bar = [
                 ["FNumber_cust", ["Make", "Model"]],
                 ["FNumber_cust", ["Make", "Model", "LensModel"]],
                  
                 ["FocalLengthIn35mmFilm", ["Make", "Model"]],
                 ["FocalLengthIn35mmFilm", ["Make", "Model", "LensModel"]],
                 
                 ["FocalLength_cust", ["Make", "Model"]],
                 ["FocalLength_cust", ["Make", "Model", "LensModel"]],

                 ["ShutterSpeed_calc", ["Make", "Model"]],
                 ["ShutterSpeed_calc", ["Make", "Model", "LensModel"]],

                 ["ISOSpeedRatings", ["Make", "Model"]],
                 ["ISOSpeedRatings", ["Make", "Model", "LensModel"]],

                 ["Orientation_cust", ["Make", "Model"]],
                 ["Orientation_cust", ["Make", "Model", "LensModel"]],
                 
                 ["LightSource_cust", ["Make", "Model"]],
                 ["LightSource_cust", ["Make", "Model", "LensModel"]],

                 ["MeteringMode_cust", ["Make", "Model"]],
                 ["MeteringMode_cust", ["Make", "Model", "LensModel"]],

                 ["ApertureValue_cust", ["Make", "Model"]],
                 ["ApertureValue_cust", ["Make", "Model", "LensModel"]],

                 ["BrightnessValue_cust", ["Make", "Model"]],
                 ["BrightnessValue_cust", ["Make", "Model", "LensModel"]],

                 ["ExposureBiasValue_cust", ["Make", "Model"]],
                 ["ExposureBiasValue_cust", ["Make", "Model", "LensModel"]],

                 ["MaxApertureValue_cust", ["Make", "Model"]],
                 ["MaxApertureValue_cust", ["Make", "Model", "LensModel"]],

                 ["Sharpness_cust", ["Make", "Model"]],
                 ["Sharpness_cust", ["Make", "Model", "LensModel"]],

                 ["SceneCaptureType_cust", ["Make", "Model"]],
                 ["SceneCaptureType_cust", ["Make", "Model", "LensModel"]],

                 
                 ["Make", ""],
                 ["Model", ""],
                 ["LensModel", ""],
                 
                 ["Year", ["Make", "Model"]],
                 ["Year", ["Make", "Model", "LensModel"]],
                  
                 ["Year_Month", ["Make", "Model"]],
                 ["Year_Month", ["Make", "Model", "LensModel"]],
                  
                 ["Month", ["Make", "Model"]],
                 ["Month", ["Make", "Model", "LensModel"]],
                  
                 ["Hour", ["Make", "Model"]],
                 ["Hour", ["Make", "Model", "LensModel"]],
                  
                 ["Week", ["Make", "Model"]],
                 ["Week", ["Make", "Model", "LensModel"]],

                 ["Hour", "ISOSpeedRatings"],
                 ["Hour", "FNumber_cust"],
                 ["Hour", "ShutterSpeed_cust"],
                 
                 ["FNumber_cust", "ISOSpeedRatings"],

                 #["ExposureTime_calc", ""],
                 # [["FNumber_cust", "ISOSpeedRatings"], ""],   ### このパターンはエラー
                 ]

    # Sort of Scatter chart
    plots_scatter = [
                    ["ExposureTime_calc", "FNumber_cust"],
                    ["Hour", "FNumber_cust"],
                    ["Hour", "ISOSpeedRatings"],
                    ["ISOSpeedRatings", "FNumber_cust"],
                    ["FocalLengthIn35mmFilm", "FNumber_cust"],
                    ["FocalLength_cust", "FNumber_cust"],
                    ["ApertureValue_cust", "FNumber_cust"],
                    ["ShutterSpeed_calc", "FNumber_cust"],
                    ["ShutterSpeed_calc", "ISOSpeedRatings"],
                    ["ShutterSpeed_calc", "ExposureTime_calc"],
                    ]

    # Sort of Pie chart
    plots_pie = [
                "Make",
                "Model",
                "LensModel",
                "FocalLengthIn35mmFilm",
                "FocalLength_cust",
                "FNumber_cust",
                "ISOSpeedRatings",
                "Year",
                "Month",
                "Week",
                 ]

    # Pivot TableをEXCELに書き出し
    saveExcelFile = dataDir + "/Photo Data " + now_dt + ".xlsx"
    writer = pd.ExcelWriter(saveExcelFile)
    df.to_excel(writer, sheet_name=now_dt)

    # - - - - - - - - - -
    # Plots Bar Chart作成
    # - - - - - - - - - -
    if plotBar == True:
        for idx, clm in plots_bar:
        
            if clm != "":
                clm2 = ""
                ds = pd.pivot_table(df, values="Count", index=idx, columns=clm, aggfunc=lambda x: len(x))

                if isinstance(clm, list):
                    n = 0
                    for val in clm:
                        n += 1
                        if n == 1: clm2 = val
                        else     : clm2 = clm2 + " & " + val
                else: clm2 = clm
        
                idx = ModifyName(idx) # Pivotを作成した後に名称変更
                fn = idx + " by " + ModifyName(clm2)
                pTitle = "x: " + ModifyName(idx) + " | y: " + ModifyName(clm2)
                lgd = True
            else:
                ds = pd.pivot_table(df, values="Count", index=idx, aggfunc=lambda x: len(x))

                idx = ModifyName(idx) # Pivotを作成した後に名称変更
                fn = idx
                pTitle = idx
                lgd = False

            # 長い名称を縮小
            fn = ReduceName(fn)

            # Write to EXCEL File
            ds.to_excel(writer, sheet_name=fn.replace("&", "_"))

            # Draw plot
            if idx in PlotBarRotate: rotate = PlotBarRotate[idx] #Rotateを個別に設定している場合
            else: rotate = plotRotate
            fontSize = 8

            ds.columns.name = ""
            ds.index.name = ""
            ds.plot(kind="bar",
                    title=pTitle,
                    grid=plotGrid,
                    legend=lgd,
                    subplots=plotSubPlots,
                    fontsize=plotFontSize,
                    rot=rotate,
                    figsize=(plotFixSizeX, plotFixSizeY),
                    stacked=True
                    )

            saveFile = dataDir + "/Pd_" + fn + ".png"
            print("> Plot:" + saveFile)
            plt.savefig(saveFile)
            plt.close()
    else: pass

    # - - - - - - - - - -
    # Plots scatter/hexbin chart作成
    # - - - - - - - - - -
    for val_x, val_y in plots_scatter:
        pTx = ModifyName(val_x)
        pTy = ModifyName(val_y)
        pTitle = str(pTx)  + " vs " + str(pTy)

        # 長い名称を縮小
        fn = ReduceName(pTitle)

        if plotScatter == True:
            # Scatter Chart
            df.plot(kind='scatter', x=val_x, y=val_y, linewidth="2", c="blue", edgecolors="blue",
                    title=pTitle,
                    grid=plotGrid,
                    legend=lgd,
                    subplots=plotSubPlots,
                    fontsize=plotFontSize,
                    #rot=plotRotate,
                    figsize=(plotFixSizeX, plotFixSizeY),
                    stacked=True
            )
            plt.xlabel(pTx)
            plt.ylabel(pTy)
            saveFile = dataDir + "/Ps_" + fn + ".png"
            print("> Plot:" + saveFile)
            plt.savefig(saveFile)
            plt.close()
        else: pass

        if plotHexbin == True:
            # Hexbin Chart
            df.plot(kind='hexbin', x=val_x, y=val_y, gridsize=30, marginals=False, cmap=cm.PuBu,
                    title=pTitle,
                    grid=plotGrid,
                    legend=lgd,
                    subplots=plotSubPlots,
                    fontsize=plotFontSize,
                    #rot=plotRotate,
                    figsize=(plotFixSizeX, plotFixSizeY),
                    stacked=True
            )

            plt.xlabel(pTx)
            plt.ylabel(pTy)
            saveFile = dataDir + "/Ph_" + fn + ".png"
            print("> Plot:" + saveFile)
            plt.savefig(saveFile)
            plt.close()
        else: pass

    # - - - - - - - - - -
    # Plots pie chart
    # - - - - - - - - - -
    if plotPie == True:
        for idx in plots_pie:
            try:
                pTitle = ModifyName(idx)
                ds = pd.pivot_table(df, values="Count", index=idx, aggfunc=lambda x: len(x))
                ds.plot(kind="pie", y="Count",
                        subplots=True,
                        title=pTitle,
                        autopct='%.1f',
                        figsize=(plotFixSizeX, plotFixSizeY),
                        counterclock=False, startangle=90,
                        pctdistance=0.8
                )
                plt.ylabel("")
                fn = ModifyName(idx)

                # 長い名称を縮小
                fn = ReduceName(fn)

                saveFile = dataDir + "/Pp_" + str(fn) + ".png"
                print("> Plot:" + saveFile)
                plt.axis('equal')
                plt.savefig(saveFile)
                plt.close()

            except AssertionError as err:
                print("*EXCEPTION:", err)

    else: pass


    # - - - - - - - - - -
    # Seaborn Chart
    # - - - - - - - - - -
    if plotSeaborn==True:
        # Seaborn PairPlot #1
        df_select = df.loc[:,["FocalLength_cust", "FNumber_cust", "ShutterSpeed_calc", "ISOSpeedRatings", "ApertureValue_cust", "ExposureBiasValue_cust", "LensModel"]]
        sb = sns.pairplot(df_select, hue="LensModel")
        saveFile = dataDir + "/Sp_Pairplot1.png"
        plt.savefig(saveFile)
        plt.close()

        # Seaborn PairPlot #2
        df_select = df.loc[:,["Hour", "FocalLength_cust", "FNumber_cust", "ShutterSpeed_calc", "ISOSpeedRatings", "LensModel"]]
        sb = sns.pairplot(df_select, hue="LensModel")
        saveFile = dataDir + "/Sp_Pairplot2.png"
        plt.savefig(saveFile)
        plt.close()


        # Seaborn JpintPlot (using scatter param)
        for val_x, val_y in plots_scatter:
            pTx = ModifyName(val_x)
            pTy = ModifyName(val_y)
            pTitle = str(pTx)  + " vs " + str(pTy)
        
        
            sb_kind = "hex" # reg, kde, hex
            sb = sns.jointplot(val_x, val_y, df, kind=sb_kind)

            # 長い名称を縮小
            fn = ReduceName(pTitle)
            saveFile = dataDir + "/Sj_" + str(fn) + ".png"
            print("> Plot:" + saveFile)
            plt.savefig(saveFile)
            plt.close()


        # Seaborn HeatMap
#       sb = sns.heatmap(df.corr())

    else: pass


    # 最後にSave
    writer.save()
    print("> Saved EXCEL file: " + saveExcelFile)


if __name__ == '__main__':
    main()

