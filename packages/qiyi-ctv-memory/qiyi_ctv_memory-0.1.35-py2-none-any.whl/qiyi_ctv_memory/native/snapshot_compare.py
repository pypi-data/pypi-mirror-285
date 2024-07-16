# coding=utf-8
import argparse
import os

import snapshot_summary
from native_memory_utils import write_records


def compare(firstFile, secondFile, outputFile):
    first_total, first_groups, first_groupRecords = snapshot_summary.snapshot_summary(
        firstFile, None)

    second_total, second_groups, second_groupRecords = snapshot_summary.snapshot_summary(
        secondFile, None)

    compare_total = second_total - first_total

    compare_groups = {}
    for key in second_groups:
        if key in first_groups:
            compare_groups[key] = second_groups[key] - first_groups[key]
        else:
            compare_groups[key] = second_groups[key]

    compare_groupRecords = {}
    for key in second_groupRecords:
        if key in first_groupRecords:
            for second_record in second_groupRecords[key]:
                find = 0
                for first_record in first_groupRecords[key]:
                    if first_record.stack == second_record.stack:
                        find = 1
                        if second_record.size > first_record.size:
                            second_record.size = second_record.size - first_record.size
                            if key in compare_groupRecords:
                                compare_groupRecords[key].append(second_record)
                            else:
                                compare_groupRecords[key] = [second_record]
                if find == 0:
                    if key in compare_groupRecords:
                        compare_groupRecords[key].append(second_record)
                    else:
                        compare_groupRecords[key] = [second_record]
        else:
            compare_groupRecords[key] = second_groupRecords[key]
    path, inputFileName = os.path.split(secondFile)
    outputFile = outputFile if outputFile else os.path.join(path, "compare_" + inputFileName)
    if os.path.exists(outputFile):
        os.remove(outputFile)
    writer = open(outputFile, 'w')

    summary = '%s\t%s\n' % (format(compare_total, ',').rjust(13, ' '), 'totals')
    if writer is not None:
        writer.write(summary)
    compare_groups_sorted = sorted(compare_groups.items(), key=lambda x: x[1], reverse=True)
    compare_groups_list = []
    for group in compare_groups_sorted:
        if group[1] > 0:
            compare_groups_list.append(group)
    for group in compare_groups_list:
        if writer is not None:
            summary_tmp = '%s\t%s\n' % (format(group[1], ',').rjust(13, ' '), group[0])
            writer.write(summary_tmp)

    for group in compare_groups_list:
        key = group[0]
        if key in compare_groupRecords:
            write_records(writer, key, compare_groupRecords[key])
    writer.close()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-f', '--firstFile', help='first file')
    argParser.add_argument('-s', '--secondFile',
                           help='second file')
    argParser.add_argument('-o', '--outputFile',
                           help='outputFile,default in secondFile folder')
    argParams = argParser.parse_args()
    compare(argParams.firstFile, argParams.secondFile, argParams.outputFile)
