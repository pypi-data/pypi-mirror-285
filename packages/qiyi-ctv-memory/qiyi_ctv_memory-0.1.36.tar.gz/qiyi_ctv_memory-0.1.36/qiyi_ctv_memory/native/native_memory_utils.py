# coding=utf-8
import os
import re

system_group = [
    'libhwui.so',
    'libsqlite.so',
    'WebViewGoogle.apk',
    'libstagefright.so',
    'libcamera_client.so',
    'libandroid_runtime.so'
]

KEY_TOTALS = 'totals'
KEY_EXTRAS = 'extras'


class Frame:
    def __init__(self, pc, path, desc):
        self.pc = pc
        self.path = path
        self.desc = desc

    def __eq__(self, b):
        return self.pc == b.pc and self.path == b.path

    def __ne__(self, b):
        return self.pc != b.pc or self.path != b.path

    def __sub__(self, b):
        return 0 if self == b else (-1 if self.pc > b.pc else 1)


class Trace:
    def __init__(self, id, size, count, stack):
        self.id = id
        self.size = int(size)
        self.count = int(count)
        self.stack = stack
        self.stack_str = ""
        if self.stack:
            for frame in self.stack:
                self.stack_str = self.stack_str + frame.pc + frame.path + frame.desc

    def __eq__(self, b):
        if len(self.stack) != len(b.stack):
            return False
        for i in range(0, len(self.stack)):
            if self.stack[i] != b.stack[i]:
                return False
        return True

    def __sub__(self, b):
        if len(self.stack) != len(b.stack):
            return -1 if len(self.stack) > len(b.stack) else 1
        for i in range(0, len(self.stack)):
            if self.stack[i] != b.stack[i]:
                return self.stack[i] - b.stack[i]
        return 0

    def get_stack_str(self):
        return self.stack_str


def getAllocSoName(record):
    default = None
    for frame in record.stack:
        so_name = frame.path
        match = re.match(r'.+\/(.+\.(so|apk|oat))', frame.path, re.M | re.I)
        if not match:
            match = re.match(r'(.+\.(so|apk|oat))', frame.path, re.M | re.I)
            if not not match:
                return match.group(0)
        else:
            so_name = match.group(1)
        if so_name == 'libnative_memory_recorder.so':
            continue
        elif frame.path.startswith('/data/'):
            return so_name
        elif so_name in system_group and not default:
            default = so_name
    return default if default else 'extras'


def write_records(writer, so_name, records):
    writer.write("\n\n-----------------------------------")
    writer.write(so_name)
    writer.write("----------------------------------------\n")
    records.sort(key=lambda x: x.size, reverse=True)
    for record in records:
        writer.write('\n%s, %s, %s\n' % (record.id, record.size, record.count))
        for frame in record.stack:
            writer.write('%s %s (%s)\n' % (frame.pc, frame.path, frame.desc))


def merge_records(records):
    if len(records) == 0:
        return []
    record = records[0]
    merged_dict = {record.get_stack_str(): record}
    for i in range(1, len(records)):
        record = records[i]
        if record.get_stack_str() in merged_dict:
            merged_dict[record.get_stack_str()].size += record.size
            merged_dict[record.get_stack_str()].count += record.count
        else:
            merged_dict[record.get_stack_str()] = record
    merged = list(merged_dict.values())
    merged.sort(key=lambda x: x.size, reverse=True)
    return merged


def parse_records(string):
    records = []
    splits = re.split(r'\n\n', string)
    for split in splits:
        try:
            match = re.compile(r'(0x[0-9a-f]+)\ (.+)\ \((.+)\)$', re.M | re.I).findall(split)
            stack = []
            for frame in match:
                stack.append(Frame(frame[0], frame[1], frame[2]))
            match = re.compile(r'(0x[0-9a-f]+),\ (\d+),\ (\d+)$', re.M | re.I).findall(split)
            records.append(Trace(match[0][0], match[0][1], match[0][2], stack))
        except Exception as e:
            print(split)
            print(e)
    return records


def sendBroadcast(broadcastCmd):
    os.system(broadcastCmd)
