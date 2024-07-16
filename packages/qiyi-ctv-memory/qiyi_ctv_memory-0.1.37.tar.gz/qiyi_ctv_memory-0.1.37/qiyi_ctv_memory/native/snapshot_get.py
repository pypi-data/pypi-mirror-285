# coding=utf-8
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import os
import sys
import time

import native_memory_utils


def pullSnapShot(cmd, package_name, target):
    native_memory_utils.sendBroadcast(
        cmd + " shell am broadcast -a com.gala.apm2.native_memory_recorder.print_snapshot " + package_name)
    time.sleep(5)
    snapshotTargetFileStr = target
    if not snapshotTargetFileStr:
        t = time.time()
        strTime = str(int(t))
        snapshotTargetFileStr = os.path.join(os.getcwd(), "snapshot_" + strTime + ".txt")
    if os.path.exists(snapshotTargetFileStr):
        os.remove(snapshotTargetFileStr)
    sdcardCmd = cmd + " pull /sdcard/Android/data/" + package_name + "/files/GalaApm/snapshot " + snapshotTargetFileStr
    os.system(sdcardCmd)
    if os.path.exists(os.path.join(os.getcwd(), snapshotTargetFileStr)):
        print(cmd + "pullSnapShot success")
        return
    dataCmd = cmd + " pull /data/data/" + package_name + "/files/GalaApm/snapshot " + snapshotTargetFileStr
    os.system(dataCmd)
    if os.path.exists(snapshotTargetFileStr):
        print(cmd + " pull snapshot success")
    else:
        print(cmd + " pull snapshot failed")


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--ip', help='device ip,if there is noly one device,ignore this')
    argParser.add_argument('-p', '--pkgname',
                           help='package name,default is com.gitvdemo.video,if don`t change package name ingore this')
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
    pullSnapShot(cmd, packageName, target)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
