# coding=utf-8
import argparse
import os

import snapshot_summary


def get_snapshots_avg(input_folder):
    if not os.path.exists(input_folder) or not os.path.isdir(input_folder):
        raise Exception('invalid folder')
    count = 0
    totalGroups = {}
    totalSize = 0
    for entry in os.listdir(input_folder):
        if entry.startswith("snapshot"):
            count = count + 1
            total, groups, groupsRecords = snapshot_summary.snapshot_summary(os.path.join(input_folder, entry),
                                                                             None)
            totalSize = totalSize + total
            for key in groups:
                if key in totalGroups:
                    totalGroups[key] = totalGroups[key] + groups[key]
                else:
                    totalGroups[key] = groups[key]
    avgSize = 0
    avgGroups = {}
    if count != 0:
        avgSize = totalSize / count
        for key in totalGroups:
            avgGroups[key] = totalGroups[key] / count
    return avgSize, avgGroups


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--inputFolder', help='snapshots folder')
    argParams = argParser.parse_args()
    avgSize, avgGroups = get_snapshots_avg(argParams.inputFolder)
    print(avgSize)
