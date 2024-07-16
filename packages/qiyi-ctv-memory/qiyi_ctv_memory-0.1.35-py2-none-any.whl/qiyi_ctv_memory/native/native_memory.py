# coding=utf-8
import os
import time

import snapshot_get
import snapshot_summary
import record_end
import record_summary
import record_start
import snapshot_compare
import record_compare


def excute(argParams, package_name):
    cmd = "adb"
    if argParams.ip:
        cmd = cmd + " -s " + argParams.ip
    target = None
    if argParams.target:
        target = argParams.target
    if argParams.action:
        action = argParams.action
        if action == "ss":
            t = time.time()
            strTime = str(int(t))
            snapshot_path = os.path.join(os.getcwd(), "snapshot_" + strTime + ".txt")
            snapshot_get.pullSnapShot(cmd, package_name, snapshot_path)
            if os.path.exists(snapshot_path):
                snapshot_summary.snapshot_summary(snapshot_path, target)
        elif action == "sr":
            t = time.time()
            strTime = str(int(t))
            record_path = os.path.join(os.getcwd(), "record_" + strTime + ".txt")
            record_end.pullRecord(cmd, package_name, record_path)
            if os.path.exists(record_path):
                record_summary.record_summary(record_path, target)
        elif action == "rs":
            record_start.startRecrd(cmd, package_name)
        elif action == "cs":
            if argParams.fi and argParams.si and os.path.exists(argParams.fi) and os.path.exists(argParams.si):
                snapshot_compare.compare(argParams.fi, argParams.si, target)
            else:
                print("参数非法或文件不存在")
        elif action == "cr":
            if argParams.fi and argParams.si and os.path.exists(argParams.fi) and os.path.exists(argParams.si):
                record_compare.compare(argParams.fi, argParams.si, target)
            else:
                print("参数非法或文件不存在")
