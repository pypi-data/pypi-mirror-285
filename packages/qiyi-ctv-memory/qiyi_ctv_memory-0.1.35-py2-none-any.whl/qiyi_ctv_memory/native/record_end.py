# coding=utf-8
import argparse
import os
import sys
import time

import native_memory_utils


def pullRecord(cmd, package_name, target):
    native_memory_utils.sendBroadcast(cmd + " shell am broadcast -a com.gala.apm2.native_memory_recorder.record_stop " + package_name)
    time.sleep(5)
    recordTargetFileStr = target
    if not recordTargetFileStr:
        t = time.time()
        strTime = str(int(t))
        recordTargetFileStr = os.path.join(os.getcwd(), "snapshot_" + strTime + ".txt")
    if os.path.exists(recordTargetFileStr):
        os.remove(recordTargetFileStr)
    sdcardCmd = cmd + " pull /sdcard/Android/data/" + package_name + "/files/GalaApm/record " + recordTargetFileStr
    os.system(sdcardCmd)
    if os.path.exists(recordTargetFileStr):
        print("pullRecord success")
        return
    dataCmd = cmd + " pull /data/data/" + package_name + "/files/GalaApm/record " + recordTargetFileStr
    os.system(dataCmd)
    if os.path.exists(recordTargetFileStr):
        print("pullRecord success")
    else:
        print("pullRecord fail")


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--ip', help='device ip,if there is only one device please ignore this')
    argParser.add_argument('-p', '--pkgname',
                           help='package name,default is com.gitvdemo.video,if don`t change package name please '
                                'ignore this')
    argParser.add_argument('-t', '--target', help='target file')
    argParams = argParser.parse_args()
    cmd = "adb "
    if argParams.ip:
        cmd = "adb -s" + sys.argv[1]
    packageName = "com.gala.video"
    if argParams.pkgname:
        packageName = argParams.pkgname
    target = None
    if argParams.target:
        target = argParams.target
    pullRecord(cmd, packageName, target)
