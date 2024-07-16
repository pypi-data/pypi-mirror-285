# coding=utf-8
import argparse
import os

import native_memory_utils
import snapshot_summary
from native_memory_utils import write_records

so_limits_high = {
    "totals": 209715200,  # 200m
    "libstagefright.so": 104857600,  # 100m
    "libandroid_runtime.so": 52428800,  # 50m
    "libhyperplayer.so": 52428800,  # 50m
    "libmcto_media_player.so": 62914560,  # 60m
    "libc++_shared.so": 26214400,  # 25m
    "libhwui.so": 52428800,  # 50m
    "libuniplayerdata.so": 15728640,  # 15m
    "libheif.so": 10485760  # 10m
}
so_limits_medium = {
    "totals": 104857600,  # 100m
    "libstagefright.so": 52428800,  # 50m
    "libandroid_runtime.so": 52428800,  # 50m
    "libhyperplayer.so": 31457280,  # 30m
    "libmcto_media_player.so": 41943040,  # 40m
    "libc++_shared.so": 20971520,  # 20m
    "libhwui.so": 52428800,  # 50m
    "libuniplayerdata.so": 15728640,  # 15m
    "libheif.so": 10485760  # 10m
}
so_limits_low = {
    "totals": 104857600,  # 100m
    "libstagefright.so": 52428800,  # 50m
    "libandroid_runtime.so": 52428800,  # 50m
    "libhyperplayer.so": 31457280,  # 30m
    "libmcto_media_player.so": 31457280,  # 30m
    "libc++_shared.so": 20971520,  # 20m
    "libhwui.so": 52428800,  # 50m
    "libuniplayerdata.so": 15728640  # 15m
}
default_so_limit = 5 * 1024 * 1024


def get_so_limits(mem_level):
    so_limits = {}
    if mem_level == 1:
        so_limits = so_limits_low
    elif mem_level == 2:
        so_limits = so_limits_medium
    else:
        so_limits = so_limits_high
    return so_limits


def check_snapshot(input, output, mem_level):
    if not input:
        raise Exception('must have a input file')
    so_limits = get_so_limits(mem_level)
    total, groups, groupsRecords = snapshot_summary.snapshot_summary(input, None)
    over_so_limits = {}
    over_so = ''
    for key in groups:
        if key in so_limits:
            if int(groups[key]) >= so_limits[key]:  # so占用超限
                over_so_limits[key] = so_limits[key]
                if over_so == '':
                    over_so = key
        elif int(groups[key]) >= default_so_limit:  # so占用超限
            over_so_limits[key] = default_so_limit
            if over_so == '':
                over_so = key
    result = ""
    writeGroups = {}
    if len(over_so_limits) > 0:
        writeGroups = over_so_limits
        for key in over_so_limits:
            result = result + "    " + key + "占用超限    size:" + str(groups[key]) + "    limit:" + str(over_so_limits[key])
    else:
        if total >= so_limits[native_memory_utils.KEY_TOTALS]:  # 没有超限的so，但是total超限
            if over_so == '':
                over_so = key
            writeGroups = groups
            result = result + "    total占用超限  size:" + str(total) + "    limit:" + str(so_limits[
                                                                                           native_memory_utils.KEY_TOTALS]) + "\n\n"
            for key in groups:
                if key != 'extras':
                    summary_tmp = '%s\t%s\n' % (format(groups[key], ',').rjust(13, ' '), key)
                    result += summary_tmp
            if 'extras' in groups:
                summary_tmp = '%s\t%s\n' % (format(groups['extras'], ',').rjust(13, ' '), 'extras')
                result += summary_tmp
    if len(result) > 0:
        path, inputFileName = os.path.split(input)
        outputFile = output if output else os.path.join(path, "check_" + inputFileName)
        if os.path.exists(outputFile):
            os.remove(outputFile)
        writer = open(outputFile, 'w')
        writer.write(result)
        for key in writeGroups:
            write_records(writer, key, groupsRecords[key])
        writer.close()
    return over_so, result, writeGroups


def is_over_size(so_name, size, mem_level):
    so_limits = get_so_limits(mem_level)
    if so_name in so_limits:
        return size > so_limits[so_name]
    return size > default_so_limit


def is_over_sizes(so_name, sizes, mem_level):
    so_limits = get_so_limits(mem_level)
    limit = 0
    if so_name in so_limits:
        limit = so_limits[so_name]
    else:
        limit = default_so_limit
    for size in sizes:
        if size > limit:
            return True
    return False


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--inputFile', help='input file')
    argParser.add_argument('-o', '--outputFile',
                           help='if not set deault is check_xxxx')
    argParams = argParser.parse_args()
    check_snapshot(argParams.inputFile, argParams.outputFile, 3)
