# coding=utf-8
import argparse
import os

from native_memory_utils import getAllocSoName, write_records, merge_records, parse_records


def print_record(outputFile, report):
    writer = open(outputFile, 'w')
    groups = {}
    groupRecords = {}
    totals = 0
    totalCount = 0
    groupCounts = {}
    for record in report:
        name = getAllocSoName(record)
        size = record.size
        groups.update({name: size + (int(groups.get(name)) if name in groups else 0)})
        totals += size
        totalCount += record.count
        if name in groupRecords:
            groupRecords.get(name).append(record)
            groupCounts[name] = groupCounts[name] + record.count
        else:
            groupRecords[name] = [record]
            groupCounts[name] = record.count
    groupCounts = sorted(groupCounts.items(), key=lambda x: x[1], reverse=True)
    if writer is not None:
        writer.write(
            '%s\t%s\t%s\n' % ("size".rjust(13, ' '), "count".rjust(7, ' '), 'soname'))
        writer.write(
            '%s\t%s\t%s\n' % (format(totals, ',').rjust(13, ' '), format(totalCount, ',').rjust(7, ' '), 'totals'))
    extras = -1
    for i in range(0, len(groupCounts)):
        if groupCounts[i][0] != 'extras':
            if writer is not None:
                writer.write('%s\t%s\t%s\n' % (
                    format(groups[groupCounts[i][0]], ',').rjust(13, ' '),
                    format(groupCounts[i][1], ',').rjust(7, ' '), groupCounts[i][0]))
        else:
            extras = i
    if extras != -1:
        if writer is not None:
            writer.write('%s\t%s\t%s\n' % (
                format(groups[groupCounts[extras][0]], ',').rjust(13, ' '),
                format(groupCounts[extras][1], ',').rjust(7, ' '), groupCounts[extras][0]))

    for i in range(0, len(groupCounts)):
        if groupCounts[i][0] != 'extras':
            if writer is not None:
                write_records(writer, groupCounts[i][0], groupRecords[groupCounts[i][0]])
    if extras != -1:
        if writer is not None:
            write_records(writer, 'extras', groupRecords['extras'])
    writer.close()
    return totals, groups, groupCounts, groupRecords


def record_summary(input, output):
    if not input:
        raise Exception('must have a input file')

    reader = open(input)
    string = reader.read()
    reader.close()

    records = parse_records(string)
    # print "parse_records finish"
    records = merge_records(records)
    # print "merge_records finish"
    path, inputFileName = os.path.split(input)
    outputFile = output if output else os.path.join(path, "summary_" + inputFileName)
    if os.path.exists(outputFile):
        os.remove(outputFile)
    return print_record(outputFile, records)


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--inputFile', help='input file')
    argParser.add_argument('-o', '--outputFile',
                           help='if not set deault is summary_xxxx')
    argParams = argParser.parse_args()
    record_summary(argParams.inputFile, argParams.outputFile)
