#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""
2019/7/31  WeiYanfeng

简化 CWinSupervisor.py ，直接传入 dictConfigByGroupId ，以便于直接启动多个进程。
"""

import sys
import os

from weberFuncs import PrintTimeMsg, GetCurrentTime, PrintAndSleep
from .winsvFuncs import LoadWinSVConfigFmDict
from .CWinSVProgram import CWinSVProgram


class CRunSupervisor:
    def __init__(self, srcfile, dictConfigByGroupId, sLongIdStr):
        # PrintTimeMsg("CRunSupervisor.__init__.srcfile=%s=" % srcfile)
        # PrintTimeMsg("CRunSupervisor.__init__.sLongIdStr=%s=" % sLongIdStr)
        self.sStartCWD = os.getcwd()
        # PrintTimeMsg("CRunSupervisor.__init__.sStartCWD=%s=" % self.sStartCWD)
        self.lsProgram = LoadWinSVConfigFmDict(srcfile, dictConfigByGroupId, sLongIdStr)
        iProgramCnt = len(self.lsProgram)
        if iProgramCnt == 0:
            PrintTimeMsg("CRunSupervisor.__init__.iProgramCnt=(%d)Error EXIT!" % iProgramCnt)
            sys.exit(-1)
        PrintTimeMsg("CRunSupervisor.__init__.iProgramCnt=(%d)!" % iProgramCnt)

        self.iCheckIntervalSeconds = 60

        iCmdCnt = 0
        self.lsWinSV = []
        for dictParam in self.lsProgram:
            oWinSV = CWinSVProgram(dictParam)
            self.lsWinSV.append(oWinSV)
            # PrintTimeMsg("  lsWinSV[%.2d]=(%s)!" % (iCmdCnt, oWinSV.sCmdExec))
            iCmdCnt += 1

    def __del__(self):
        pass

    def LoopAndWatchPrograms(self):
        iLoopCnt = 0
        while True:
            os.chdir(self.sStartCWD)  # 回到启动时的目录
            iStart, iStop = 0, 0
            for oWinSV in self.lsWinSV:
                iChg = oWinSV.CheckAndRunOneCmd(iLoopCnt)
                if iChg > 0:
                    iStart += 1
                if iChg < 0:
                    iStop += 1
            if iStart > 0 or iStop > 0:
                PrintTimeMsg("  >>(%s)#%d.iStart=%s,iStop=%s!" % (
                    self.sStartCWD, iLoopCnt, iStart, iStop))
            else:
                PrintAndSleep(self.iCheckIntervalSeconds,
                              "  >>(%s)#%d" % (self.sStartCWD, iLoopCnt),
                              iLoopCnt % 10 == 0)
            iLoopCnt += 1


def mainCRunSupervisor(srcfile, dictConfigByGroupId, sLongIdStr):
    ws = CRunSupervisor(srcfile, dictConfigByGroupId, sLongIdStr)
    ws.LoopAndWatchPrograms()

# --------------------------------------
if __name__ == '__main__':
    dictConfigByGroupId = {
        'group_One': {  # 单一程序组
            'logDir': '../log',
            'workDir': './',
            'err2out': True,
            'ping_qq': {
                'cmdExec': 'ping www.qq.com',
                'cmdTitle': 'ping_qq test',
            },
        },
    }
    sLongIdStr = 'group_One'
    mainCRunSupervisor(__file__, dictConfigByGroupId, sLongIdStr)
