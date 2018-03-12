#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

class WriteLog:
    def WriteLog(self, logs):

        # 日付の取得
        now = datetime.datetime.now()
        now_dt = str(now.year) + "/" + str(now.month).rjust(2,'0')  + "/" + str(now.day).rjust(2,'0')  + " " + \
            str(now.hour).rjust(2,'0')  + ":" + str(now.minute) .rjust(2,'0') + ":" + str(now.second).rjust(2,'0')
        now_date = str(now.year) + str(now.month).rjust(2,'0')  + str(now.day).rjust(2,'0') 

        # Check directory and create if required
        if os.path.exists("./log") == False:
            os.mkdir("./log")

        logf = open("./log/MPD " + now_date + ".txt", "a")

        logf.write(now_dt + ":" + logs + "\n")

        logf.close()

        # Terminalに表示
        # print(logs)

if __name__ == '__main__':

    main()
