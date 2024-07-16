# -*- coding: utf-8 -*--
import argparse
import codecs
import datetime
import json
import os
import threading
from qiyi_ctv_memory.java import javaHeap

from Adb import Adb

from native import snapshot_get, snapshot_check


def trigger_native_dump(adb, deviceIp, package_name, outputPath, outputFile, memoryLevel, shared_msg):
    print("Triggering native.dump")
    memory_level_int = 0
    if memoryLevel == 'high':
        memory_level_int = 3
    elif memoryLevel == 'medium':
        memory_level_int = 2
    else:
        memory_level_int = 1
    snapshot_path = os.path.join(outputPath, "snapshot")
    snapshot_check_result_path = os.path.join(outputPath, "snapshot_check_result")
    snapshot_get.pullSnapShot("adb -s {} ".format(deviceIp), package_name, snapshot_path)
    if not os.path.exists(snapshot_path):
        return
    over_size_so, result, groups = snapshot_check.check_snapshot(snapshot_path,
                                                                 snapshot_check_result_path,
                                                                 memory_level_int)
    if over_size_so != "":
        mac = adb.shell_output("cat /sys/class/net/wlan0/address")
        json_list = []
        if os.path.exists(outputFile):
            with codecs.open(outputFile, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content.strip()) > 0:
                    json_list = json.loads(content)
        new_node = {
            u"title": u"native占用异常-{}".format(over_size_so),
            u"level": u"2",
            u"type": u"native",
            u"owner": u"wangjianqiang@qiyi.com",
            u"msg": shared_msg + result,
            u"signature": mac + "--" + result
        }
        json_list.append(new_node)
        with codecs.open(outputFile, 'w', encoding='utf-8') as file:
            json.dump(json_list, file, ensure_ascii=False, indent=4)


def trigger_total_memory_dump(adb, outputFile, shared_msg, process_total_mb):
    mac = adb.shell_output("cat /sys/class/net/wlan0/address")
    print("trigger_total_memory_dump, mac = {}").format(mac)
    json_list = []
    if os.path.exists(outputFile):
        with codecs.open(outputFile, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content.strip()) > 0:
                json_list = json.loads(content)
    new_node = {
        u"title": u"pss total 占用异常-{}".format(process_total_mb),
        u"level": u"2",
        u"type": u"total",
        u"owner": u"maoyongpeng@qiyi.com",
        u"msg": shared_msg,
        u"signature": mac+u"--pss total out size"
    }
    json_list.append(new_node)
    with codecs.open(outputFile, 'w', encoding='utf-8') as file:
        json.dump(json_list, file, ensure_ascii=False, indent=4)




def classify_device(total_memory_mb):
    if total_memory_mb > 2048:
        return 'high'
    elif 1024 <= total_memory_mb <= 2048:
        return 'medium'
    else:
        return 'low'


thresholds = {
    'high': {'dalvik': 80, 'native': 150, 'total': 450},
    'medium': {'dalvik': 60, 'native': 100, 'total': 300},
    'low': {'dalvik': 40, 'native': 50, 'total': 200}
}


def parse_java(adb, hprof, name, outputPath, mappingPath, out_size, outputFile, memoryLevel,
               shared_msg):
    hprof = javaHeap.pullHprof(adb, hprof, name, outputPath)
    mac = adb.shell_output("cat /sys/class/net/wlan0/address")
    if hprof == 'null':
        return
    if out_size:
        json = javaHeap.parseAll(hprof, outputPath, mappingPath, memoryLevel)
    else:
        json = javaHeap.parseLeak(hprof, outputPath, mappingPath, memoryLevel)
    javaHeap.parse_json_and_find_bug(json, outputFile, out_size, shared_msg, memoryLevel, mac)


def check_memory(mappingPath, is_timed, outputPath, deviceIp, total_memory_mb, process_total_mb,
                 dalvik_memory_mb, native_memory_mb):
    # Device classification
    memoryLevel = classify_device(total_memory_mb)
    now = datetime.datetime.now()
    # 格式化当前时间
    formatted_time = now.strftime("%Y.%m.%d-%H.%M.%S.%f")[:-3]
    outputFile = os.path.join(outputPath, "memory_warn_{}.json".format(formatted_time))

    adb = Adb(deviceIp)
    package_name = adb.get_current_package_name()

    shared_msg = (
        u"设备内存：{total_memory_mb}MB\n"
        u"进程内存：{process_total_mb}MB\n"
        u"java内存：{dalvik_memory_mb}MB\n"
        u"native内存：{native_memory_mb}MB\n"
    ).format(
        total_memory_mb=total_memory_mb,
        process_total_mb=process_total_mb,
        dalvik_memory_mb=dalvik_memory_mb,
        native_memory_mb=native_memory_mb
    )
    if is_timed:
        hprof = javaHeap.dumpHprof(adb, package_name)
        # 这里添加dumpnative，后边执行比较慢
        trigger_native_dump(adb, deviceIp, package_name, outputPath, outputFile, memoryLevel, shared_msg)
        javaThread = threading.Thread(
            target=parse_java,
            args=(adb, hprof, str(formatted_time), outputPath, mappingPath, False, outputFile,
                  memoryLevel, shared_msg)
        )
        javaThread.start()
        javaThread.join()
    else:
        # Get thresholds for the current device class
        current_thresholds = thresholds[memoryLevel]

        # Check dalvik memory
        if dalvik_memory_mb > current_thresholds['dalvik']:
            hprof = javaHeap.dumpHprof(adb, package_name)
            javaThread = threading.Thread(
                target=parse_java,
                args=(adb, hprof, str(formatted_time), outputPath, mappingPath, True, outputFile,
                      memoryLevel, shared_msg)
            )
            javaThread.start()
            javaThread.join()
        # Check native memory
        if native_memory_mb > current_thresholds['native']:
            trigger_native_dump(adb, deviceIp, package_name, outputPath, outputFile, memoryLevel,
                                shared_msg)
        # Check total process memory
        if process_total_mb > current_thresholds['total']:
            trigger_total_memory_dump(adb, outputFile, shared_msg, process_total_mb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Memory monitoring script for monkey testing.")
    parser.add_argument('-t', '--timed', action='store_true', help="Whether it is a timed trigger")
    parser.add_argument('-m', '--total_memory', type=int, required=True,
                        help="Total device memory in MB")
    parser.add_argument('-p', '--process_memory', type=int, required=True,
                        help="Total process memory in MB")
    parser.add_argument('-d', '--dalvik_memory', type=int, required=True,
                        help="Dalvik process memory in MB")
    parser.add_argument('-n', '--native_memory', type=int, required=True,
                        help="Native process memory in MB")

    args = parser.parse_args()

    # check_memory_triggers(args.timed, args.total_memory, args.process_memory, args.dalvik_memory, args.native_memory)
