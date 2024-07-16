# coding=utf-8
import argparse
import os

from native_memory_utils import getAllocSoName, merge_records, parse_records


def print_snapshot(outputFile, report):
    writer = open(outputFile, 'w')
    groups = {}
    groupRecords = {}
    totals = 0
    for record in report:
        name = getAllocSoName(record)
        size = record.size
        groups.update({name: size + (int(groups.get(name)) if name in groups else 0)})
        totals += size
        if name in groupRecords:
            groupRecords.get(name).append(record)
        else:
            groupRecords[name] = [record]
    groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
    if writer is not None:
        writer.write('%s\t%s\n' % (format(totals, ',').rjust(13, ' '), 'totals'))
    extras = -1
    for i in range(0, len(groups)):
        if groups[i][0] != 'extras':
            if writer is not None:
                writer.write('%s\t%s\n' % (format(groups[i][1], ',').rjust(13, ' '), groups[i][0]))
        else:
            extras = i
    if extras != -1:
        if writer is not None:
            writer.write('%s\t%s\n' % (format(groups[extras][1], ',').rjust(13, ' '), groups[extras][0]))

    report.sort(key=lambda x: x.size, reverse=True)
    for record in report:
        if writer is not None:
            writer.write('\n%s, %s, %s\n' % (record.id, record.size, record.count))
            for frame in record.stack:
                writer.write('%s %s (%s)\n' % (frame.pc, frame.path, frame.desc))
    writer.close()
    return totals, dict(groups), groupRecords


def snapshot_summary(input, output):
    if not input:
        raise Exception('must have a input file')
    reader = open(input)
    string = reader.read()
    reader.close()

    records = parse_records(string)
    records = merge_records(records)
    path, inputFileName = os.path.split(input)
    outputFile = output if output else os.path.join(path, "summary_" + inputFileName)
    if os.path.exists(outputFile):
        os.remove(outputFile)
    return print_snapshot(outputFile, records)


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--inputFile', help='input file')
    argParser.add_argument('-o', '--outputFile',
                           help='if not set deault is summary_xxxx')
    argParams = argParser.parse_args()
    snapshot_summary(argParams.inputFile, argParams.outputFile)
