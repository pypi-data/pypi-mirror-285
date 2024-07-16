# coding=utf-8
import argparse
import os

import numpy as np

import snapshot_summary
from native_memory_utils import write_records

LEAK_SLOP = 0.1763  # tan10


def get_slop(list):
    index = [i for i in range(1, len(list) + 1)]
    coef = np.polyfit(index, list, 1)
    slop = coef[0]
    return slop


def getSoUsedSlops(groupList):
    transList = {}
    soList = []
    soSlops = {}
    for group in groupList:
        for key in group:
            if key not in soList:
                soList.append(key)

    for group in groupList:
        for key in soList:
            if key in group:
                if key in transList:
                    transList[key].append(group[key])
                else:
                    transList[key] = [group[key]]
            else:
                if key in transList:
                    transList[key].append(0)
                else:
                    transList[key] = [0]
    for so in soList:
        soSlops[so] = get_slop(transList[so])
    return soSlops


def is_leak(list):
    slop = get_slop(list)
    print("leak slop = " + str(slop))
    return slop > LEAK_SLOP


def leak_detect(input_folder, outputFile):
    if not os.path.exists(input_folder) or not os.path.isdir(input_folder):
        raise Exception('invalid folder')
    totalList = []
    groupList = []
    groupRecordsList = []
    count = 0
    fileList = os.listdir(input_folder)
    fileList = sorted(fileList, key=lambda x: os.path.getctime(os.path.join(input_folder, x)))
    for entry in fileList:
        if entry.startswith("snapshot"):
            count = count + 1
            total, groups, groupsRecords = snapshot_summary.snapshot_summary(os.path.join(input_folder, entry),
                                                                             None)
            totalList.append(total)
            groupList.append(groups)
            groupRecordsList.append(groupsRecords)
    totalList = [2, 3, 4, 5]  # 测试代码
    result = ""
    if is_leak(totalList):
        soSlops = getSoUsedSlops(groupList)
        leakSoList = []
        for so in soSlops:
            if soSlops[so] > LEAK_SLOP:
                leakSoList.append(so)
        if len(leakSoList) == 0:
            result = "native占用一直上涨，未发现泄漏so，total：" + str(totalList[-1])
        else:
            result = "    泄漏so"
            for so in leakSoList:
                result = result + "\n    " + so + "：" + groupList[-1][so]
        outputFile = outputFile if outputFile else os.path.join(input_folder, "leak_native_so.txt")
        if os.path.exists(outputFile):
            os.remove(outputFile)
        writer = open(outputFile, 'w')
        writer.write(result)
        if len(leakSoList) > 0:
            for so in leakSoList:
                write_records(writer, so, groupRecordsList[-1][so])
        else:
            writer.write('%s\t%s\n' % (format(totalList[-1], ',').rjust(13, ' '), 'total'))
            for key in groupList[-1]:
                if key != 'extras':
                    writer.write('%s\t%s\n' % (format(groupList[-1][key], ',').rjust(13, ' '), key))
            if 'extras' in groupList[-1]:
                writer.write('%s\t%s\n' % (format(groupList[-1]['extras'], ',').rjust(13, ' '), 'extras'))
            for key in groupList[-1]:  # 使用groupList是因为groupList中数据是经过大小排序的
                write_records(writer, key, groupRecordsList[-1][key])
        writer.close()
    return result


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--inputFolder', help='snapshots folder')
    argParser.add_argument('-o', '--outputFile', help='outfile')
    argParams = argParser.parse_args()
    leak_detect(argParams.inputFolder, argParams.outputFile)
