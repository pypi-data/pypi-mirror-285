# coding=utf-8
import argparse
import sys

import native_memory_utils


def startRecrd(cmd, package_name):
    native_memory_utils.sendBroadcast(
        cmd + " shell am broadcast -a com.gala.apm2.native_memory_recorder.record_start " + package_name)


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--ip', help='device ip,if there is noly one device,ignore this')
    argParser.add_argument('-p', '--pkgname',
                           help='package name,default is com.gitvdemo.video,if don`t change package name ingore this')
    argParams = argParser.parse_args()
    cmd = "adb "
    if argParams.ip:
        cmd = "adb -s" + sys.argv[1]
    packageName = "com.gala.video"
    if argParams.pkgname:
        packageName = argParams.pkgname
    startRecrd(cmd, packageName)
