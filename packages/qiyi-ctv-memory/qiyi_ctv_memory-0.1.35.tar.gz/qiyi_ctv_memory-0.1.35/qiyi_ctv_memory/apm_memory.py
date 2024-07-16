# -*- coding: utf-8 -*--
import argparse
import datetime
import subprocess

import pkg_resources
from qiyi_ctv_memory.native import native_memory

from qiyi_ctv_memory.Adb import Adb
from qiyi_ctv_memory.java import javaHeap


def parse_arguments():
    parser = argparse.ArgumentParser(description='argument')
    parser.add_argument('-c', '--categories', dest='CATEGORIES',  default='', help='what do you want to do?')
    parser.add_argument('-o', '--output',  dest='OUTPUT', default='', help='output path')
    parser.add_argument('-f', '--focus',  dest='FOCUS', default='', help='focus class')
    parser.add_argument('-m', '--mapping',  dest='MAPPING', default='', help='apk mapping file')

    parser.add_argument('-i', '--ip', help='device ip,if there is only one device please ignore this')
    parser.add_argument('-p', '--pkgname',
                           help='package name,default is com.gitvdemo.video,if don`t change package name please '
                                'ignore this')
    parser.add_argument('-t', '--target', help='target file')
    parser.add_argument('-a', '--action', help='action to do')
    parser.add_argument('-fi', '--fi', help='first input')
    parser.add_argument('-si', '--si', help='second input')
    args, unknown_args = parser.parse_known_args()
    return args, unknown_args

def main():
    args, unknown_args = parse_arguments()
    categories = args.CATEGORIES
    outputPath = args.OUTPUT
    if categories == 'native':
        adb = None
        if args.ip:
            adb = Adb(args.ip)
        else:
            adb = Adb()
        package_name = adb.get_current_package_name()
        if args.pkgname:
            package_name = args.pkgname
        else:
            if package_name == '':
                package_name = 'com.gitvdemo.video'
        native_memory.excute(args, package_name)
    else:
        adb = Adb()
        package_name = adb.get_current_package_name()
        now = datetime.datetime.now()
        # 格式化当前时间
        formatted_time = now.strftime("%Y.%m.%d-%H.%M.%S.%f")[:-3]
        hprof = javaHeap.dumpHprof(adb, package_name)
        hprof = javaHeap.pullHprof(adb, hprof, str(formatted_time), outputPath)
        mappingPath = args.MAPPING
        if categories == 'leak':
            javaHeap.parseLeak(hprof, outputPath, mappingPath, 'low')
        elif categories == 'javadetail':
            javaHeap.parseAll(hprof, outputPath, mappingPath, 'high')
        elif categories == 'focus':
            focus = args.FOCUS
            javaHeap.parseFocus(hprof, outputPath, mappingPath, focus)
        pass

if __name__ == "__main__":
    main()
