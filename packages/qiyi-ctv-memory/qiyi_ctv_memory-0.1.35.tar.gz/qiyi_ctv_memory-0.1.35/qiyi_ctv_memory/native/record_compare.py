# coding=utf-8
import argparse
import os

import record_summary
from native_memory_utils import write_records

MIN_COUNT = 1000
MIN_PER = 10


def compare(firstFile, secondFile, outputFile):
    first_total, first_groups, first_group_counts, first_groupRecords = record_summary.record_summary(
        firstFile, None)

    second_total, second_groups, second_group_counts, second_groupRecords = record_summary.record_summary(
        secondFile, None)
    recordSos = {}
    first_group_counts_dict = dict(first_group_counts)
    second_group_counts_dict = dict(second_group_counts)
    for key in second_group_counts_dict:
        first_count = first_group_counts_dict[key]
        second_count = second_group_counts_dict[key]
        if second_count > MIN_COUNT and first_count > MIN_COUNT:
            percent = (second_count - first_count) * 100 / first_count
            if percent > MIN_PER:
                recordSos[key] = percent
    result = ""
    if len(recordSos) > 0:
        for so in recordSos:
            result = "    " + so + "分配次数增长超过10%，前值：" + str(first_group_counts_dict[so]) + "  新值：" + str(second_group_counts_dict[so]) + "\n"
        path, inputFileName = os.path.split(secondFile)
        outputFile = outputFile if outputFile else os.path.join(path, "compare_" + inputFileName)
        if os.path.exists(outputFile):
            os.remove(outputFile)
        writer = open(outputFile, 'w')
        writer.write(result)
        for so in recordSos:
            write_records(writer, so, second_groupRecords[so])



if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-f', '--firstFile', help='first file')
    argParser.add_argument('-s', '--secondFile',
                           help='second file')
    argParser.add_argument('-o', '--outputFile',
                           help='outputFile,default in secondFile folder')
    argParams = argParser.parse_args()
    compare(argParams.firstFile, argParams.secondFile, argParams.outputFile)
