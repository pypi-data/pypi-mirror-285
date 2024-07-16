# weberWinSV/__main__.py
# python -m weberWinSV 入口程序

import sys
import os
from .CWinSupervisor import StartCWinSupervisor


def _startWinSV(sSettingPyFN, sGroupKeyName, sDictVarName):
    sWorkDir = os.getcwd()
    sFullFN = os.path.join(sWorkDir, sSettingPyFN)
    if not os.path.exists(sFullFN):
        print(f"_startWinSV.sFullFN={sFullFN}=NotExist!")
        return False
    # sPythonFileName = os.path.basename(sSettingPyFullFN)
    # print(f'_startWinSV.sPythonFileName={sPythonFileName}=')
    StartCWinSupervisor(sFullFN, sSettingPyFN, sDictVarName, sGroupKeyName)
    return True


if __name__ == "__main__":
    # 调用包内的函数或执行其他初始化代码
    sSettingPyFN = 'winsv4Run.py'
    sGroupKeyName = 'GroupId4Run'
    sDictVarName = 'gDictConfigByGroupId'
    if len(sys.argv) >= 2:
        sSettingPyFN = sys.argv[1]
        if len(sys.argv) >= 3:
            sGroupKeyName = sys.argv[2]
            if len(sys.argv) >= 4:
                sDictVarName = sys.argv[3]
    if not _startWinSV(sSettingPyFN, sGroupKeyName, sDictVarName):
        print("\nChange the directory to the directory where winsv4Run.py is located.\n\n")
        print("python -m weberWinSV winsv4Run.py")


