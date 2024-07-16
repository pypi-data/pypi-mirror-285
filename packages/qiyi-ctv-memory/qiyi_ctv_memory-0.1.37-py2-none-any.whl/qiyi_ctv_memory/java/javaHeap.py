# -*- coding: utf-8 -*--
import argparse
import json
import operator
import os
import time
import subprocess
import codecs
import pkg_resources
from qiyi_ctv_memory.Adb import Adb


thresholds = {
    'high': {'android.graphics.Bitmap': 50, 'java.lang.String': 15, 'com.gala.apm2.trace.core.AppMethodBeat': 8, 'other':5},
    'medium': {'android.graphics.Bitmap': 40, 'java.lang.String': 10, 'com.gala.apm2.trace.core.AppMethodBeat': 8, 'other':5},
    'low': {'android.graphics.Bitmap': 25, 'java.lang.String': 5, 'com.gala.apm2.trace.core.AppMethodBeat': 4, 'other':5}
}

def get_threshold(level, name):
    # 尝试获取指定名称的阈值，如果不存在则获取 'other' 的阈值
    return thresholds[level].get(name, thresholds[level].get('other'))

def pullHprof(adb, java_heap_file, name, output):
    dump_complete = checkFileDumpCompleted(adb, java_heap_file)
    if dump_complete:
        output_runtime = name + ".hprof"
        output_runtime = os.path.join(output, output_runtime)
        stdout, stderr, return_code = adb.pull(java_heap_file, output_runtime)
        if stdout:
            print("Standard Output:\n{}".format(stdout))
        if stderr:
            print("Standard Error:\n{}".format(stderr))
        if wait_for_file(output_runtime):
            adb.shell_output("rm -rf " + java_heap_file + "*")
        else:
            print("Failed to pull file {} within the timeout period.".format(output_runtime))
            return "null"

    return output_runtime

def dumpHprof(adb, pkg_name):
    adb.shelltimeout('am broadcast -a com.gala.video.action.DUMPMEM_JAVA {}'.format(pkg_name))
    pid = adb.get_pid(pkg_name)
    heap_dir = '/sdcard/Android/data/' + pkg_name + '/files/GalaApm/dump/'
    java_heap_file = heap_dir + 'runtime.hprof_' + pid
    return java_heap_file

def wait_for_file(filepath, timeout=120, poll_interval=3):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(filepath):
            # 检查文件是否完全写入（大小稳定）
            initial_size = os.path.getsize(filepath)
            time.sleep(poll_interval)
            if os.path.getsize(filepath) == initial_size:
                return True
        time.sleep(poll_interval)
    return False

def checkFileDumpCompleted(adb, src_file, count=5):
    check_count = 0
    last_params = None
    total_count = 0
    while total_count < 20:
        total_count += 1
        time.sleep(3)
        readlines = adb.shell_output('ls -l {}'.format(src_file))
        if readlines:
            ret = readlines[0]
            if ret is not None:
                if last_params is not None:
                    params = ret.split()
                    if operator.eq(params,last_params):
                        check_count = check_count + 1
                        if check_count >= count:
                            return True
                        continue
                    else:
                        check_count = 0
                        last_params = ret.split()
                        continue
                else:
                    check_count = 0
                    last_params = ret.split()
                    continue
            else:
                check_count += 1
                if check_count > 3:
                    return False
    return True

def getInstanceName(instance):
    at_position = instance.find('@')

    if at_position != -1:
        return instance[:at_position]
    else:
        return instance

def parse_json_and_find_bug(input_file, output_file, out_size, shared_msg, memoryLevel, mac):
    with codecs.open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    new_json_list = []
    if os.path.exists(output_file):
        with codecs.open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content.strip()) > 0:
                new_json_list = json.loads(content)

    if "LeakBitmap" in data:
        for item in data["LeakBitmap"]:
            if item.get("size", 0) > 200 * 1024:
                msg = (
                    u"所属文件：{path}\n"
                    u"bitmap实例：{instance}\n"
                    u"所属view：{views}\n"
                    u"关联的context：{contexts}\n"
                    u"分辨率：{resolution}\n"
                    u"占用内存：{size_kb} KB\n"
                    u"bitmap最短gc路径：{trace}\n"
                ).format(
                    path = os.path.splitext(os.path.basename(input_file))[0],
                    instance=item.get("instance", ""),
                    views=item.get("views", ""),
                    contexts=item.get("contexts", ""),
                    resolution=item.get("resolution", ""),
                    size_kb=item.get("size", 0) / 1024,
                    trace=item.get("trace", "").replace(u"<br/>", u"\n")
                )
                new_node = {
                    u"title": u"图片未释放--" + item.get("instance", ""),
                    u"level": u"2",
                    u"type": u"java",
                    u"owner": item.get("contexts", ""),
                    u"msg": shared_msg+msg,
                    u"signature":u"bitmap-"+item.get("resolution", "")+u"-"+getInstanceName(item.get("views", ""))
                                 +u"-"+item.get("trace", "")
                }
                new_json_list.append(new_node)
    if "LeakActivity" in data:
        for item in data["LeakActivity"]:
            msg = (
                u"泄露的activity：{instances}\n"
                u"trace：{trace}\n"
            ).format(
                instances=item.get("instances", "").replace(u",", u"\n"),
                trace=item.get("trace", "")
            )

            new_node = {
                u"title": u"activity泄露--" + item.get("instances", ""),
                u"level": u"1",
                u"type": u"java",
                u"owner": item.get("instances", ""),
                u"msg": shared_msg+msg,
                u"signature":u"activity-"+getInstanceName(item.get("instances", ""))+u"-"+item.get("trace", "")
            }
            new_json_list.append(new_node)

    if out_size:
        signature = mac+"--"
        msg = (
            u"hprof细分： javaTotal：{javaTotal}\n"
            u"nativeTotal：{nativeTotal}\n"
        ).format(
            javaTotal=data.get('javaTotal', 0),
            nativeTotal=data.get('nativeTotal', 0)
        )
        if "Classs" in data:
            for entry in data.get("Classs", []):
                instance = entry.get("instance", "")
                size = entry.get("size", 0) / 1024 / 1024
                threshold_size = get_threshold(memoryLevel, instance)
                if size > threshold_size:
                    tmp = u"{} total size is larger than {}MB({}MB)".format(instance,str(threshold_size),str(size))
                    signature += tmp
                    msg += tmp
                    if instance == "android.graphics.Bitmap" :
                        sorted_bitmaps = sorted(data.get("largerBitmap", []), key=lambda x: x["size"], reverse=True)
                        top_bitmaps = sorted_bitmaps[:5]

                        top_bitmap_str = u"\n".join([
                            u"instance: {instance}, size: {size} KB, resolution: {resolution}".format(
                                instance=b["instance"].decode('utf-8'),
                                size=b["size"] / 1024.0,
                                resolution=b["resolution"].decode('utf-8')
                            ) for b in top_bitmaps
                        ])
                        msg += top_bitmap_str
        new_node = {
            u"title": u"java heap 过大",
            u"level": u"2",
            u"type": u"java",
            u"owner": u"maoyongpeng@qiyi.com",
            u"msg": shared_msg+msg,
            u"signature": u"java heap 过大  "+signature
        }
        new_json_list.append(new_node)

    with codecs.open(output_file, 'w', encoding='utf-8') as file:
        json.dump(new_json_list, file, ensure_ascii=False, indent=4)

jar_path = pkg_resources.resource_filename('qiyi_ctv_memory', 'java/heap_analyzer.jar')

def parseLeak(hprof, outputPath, mapping, memoryLevel):
    leak = 'activity'
    if memoryLevel == 'low':
        leak = leak + ',bitmap'
    cmd = ["java", "-jar", jar_path, "-i", hprof, "-o", outputPath, "-m", mapping, "-l", leak]
    print("Executing Java command: " + " ".join(cmd))
    subprocess.check_call(cmd)
    return hprof.replace('.hprof', '.json')

def parseAll(hprof, outputPath, mapping, memoryLevel):
    leak = 'activity'
    if memoryLevel == 'low':
        leak = leak + ',bitmap'
    cmd = ["java", "-jar", jar_path, "-i", hprof, "-o", outputPath, "-m", mapping, "-l", leak,
           "-d","10", "-b","20"]
    print("Executing Java command: " + " ".join(cmd))
    subprocess.check_call(cmd)
    return hprof.replace('.hprof', '.json')

def parseFocus(hprof, outputPath, mapping, focus):
    cmd = ["java", "-jar", jar_path, "-i", hprof, "-o", outputPath, "-m", mapping, "-f", focus]
    print("Executing Java command: " + " ".join(cmd))
    subprocess.check_call(cmd)
    return hprof.replace('.hprof', '.json')

def parse(hprof, outputPath, mapping, arguments):
    java_command = ["java", "-jar", "heap_analyzer", "-i", hprof, "-o", outputPath, "-m", mapping] + arguments
    process = subprocess.Popen(
        java_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    json_name = hprof.replace('.hprof', '.json')
    abs_file_path = os.path.join(outputPath, json_name)
    detail_info = None
    if os.path.exists(abs_file_path):
        with open(abs_file_path, mode='r') as reader:
            detail_info = reader.read()

    # try:
    #     # parse_results = process_json(detail_info) if detail_info else None
    # except Exception as e:
    #     print(e)

def parse_arguments():
    parser = argparse.ArgumentParser(description='argument')
    parser.add_argument('-m', '--mapping', dest='MAPPING',  default='', help='apk mapping')
    parser.add_argument('-o', '--output',  dest='OUTPUT', default='', help='output path')
    parser.add_argument('-n', '--name', dest='NAME', default='', help='test name')
    parser.add_argument('-d', '--device',  dest='DEVICE', default='', help='device ip')
    # remove dest='ACTION', since it is not being used in this script

    args, unknown_args = parser.parse_known_args()
    return args, unknown_args

if __name__ == "__main__":
    args, jar_args = parse_arguments()
    device = args.DEVICE
    name = args.NAME
    outputPath = args.OUTPUT
    mapping = args.MAPPING

    adb = Adb(device)
    # hprof = dumpHprof(adb, name, outputPath)
    # if hprof:
    #     parse(hprof, outputPath, mapping, jar_args)