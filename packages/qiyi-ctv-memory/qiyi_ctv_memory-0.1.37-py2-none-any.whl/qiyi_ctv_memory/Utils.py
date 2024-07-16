# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'xuezhenhua@qiyi.com'

"""
@author:xuezhenhua@qiyi.com
@time: 18/1/8 下午2:52
"""
import time
import datetime
import os
import sys
import subprocess
import platform
import shlex
# import requests
# import json
#
# from PIL import Image, ImageDraw

DEVICE_MODEL = {}

def kill_logcat_on_win(device):
    kill_pid = []
    cmd_res = subprocess.check_output("wmic process where caption='adb.exe' get commandline,processId")
    for _ in cmd_res.split('\r\r\n'):
        if device + " logcat" in _:
            kill_pid.append(_.strip().split(" ")[-1])
    for pid in kill_pid:
        subprocess.check_output('TASKKILL /F /PID ' + pid)


def shorten_device(device):
    if '/' in str(device):
        device = str(device).replace('/', '_')
    model = None
    if device in DEVICE_MODEL:
        model = DEVICE_MODEL.get(device)
    else:
        model = get_android_model(device)
        DEVICE_MODEL[device] = model
    device_short = str(device).split('.')[3].split(":")[0] if ':' in str(device) else str(device)
    return device_short + "@{}".format(model)
    # return str(device).replace(':', '@').split('.')[3] if ':' in str(device) else str(device)

def get_android_model(device):
    return __shell_output(device, 'getprop ro.product.model').replace(" ","_").replace("\n","").replace("\r","")

def __shell_output(device, args):
    if device is None or device == "":
        cmd = 'adb shell {}'.format(args)
    else:
        cmd = 'adb -s {} shell {}'.format(device, args)
    # print("shell cmd:" + cmd)
    return os.popen(cmd).read()

def mid_y(e):
    return e.location['y'] + e.size['height'] / 2


def mid_x(e):
    return e.location['x'] + e.size['width']/2


def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def e_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def kill_by_pid(pid):
    try:
        sysstr = platform.system()
        pid = str(pid)
        if sysstr == 'Windows':
            output, err = subprocess.Popen(['TASKKILL', '/F', '/T', '/PID', pid],
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
            if err:
                e_print(str(err).decode('gbk').encode('utf-8').strip())
        else:
            # mac
            os.popen("kill -9 {0}".format(pid))
    except:
        pass


def kill_by_port(port):
    sysstr = platform.system()
    if sysstr == 'Windows':
        out_bytes = subprocess.check_output(['netstat', '-ano'])
        p = subprocess.Popen(['findstr', str(port)],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        stdout, stderr = p.communicate(out_bytes)
        lines = stdout.splitlines()
        p.kill()
        pid = ''
        for line in lines:
            if line.split()[3] == 'LISTENING':
                pid = line.split()[4]
                break
        if len(pid) > 0:
            try:
                subprocess.check_output(['TASKKILL', '/F', '/T', '/PID', pid])
            except subprocess.CalledProcessError as e:
                print('command "%s" return with error (code %s): %s' %
                      (e.cmd, e.returncode, e.output))
    else:
        # mac
        p = subprocess.Popen(['lsof', '-i', ':%d' % port], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode == 0:
            p = subprocess.Popen(shlex.split("awk '/(LISTEN)/{print $2}'"),
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            pid, err = p.communicate(out)
            print(pid)
            # print plists[0]
            cmd = "kill -9 {0}".format(pid)
            print(cmd)
            subprocess.call(shlex.split(cmd))


# 时间类型格式化操作
def format_time_value(time_value):
    count = str(time_value).count(':')
    if count == 1:
        time_value = datetime.datetime.strptime(time_value, "%M:%S")
    else:
        time_value = datetime.datetime.strptime(time_value, "%H:%M:%S")
    return time_value


def add_time(time_value, seconds):
    result = (format_time_value(time_value) + datetime.timedelta(seconds=seconds))
    h, m, s = result.strftime('%H:%M:%S').split(':')
    return '%s:%s:%s' % (h, m, s)


# 获取时间间隔，单位是秒
def get_time_interval(first_time_value, second_time_value):
    first_time_value = format_time_value(first_time_value)
    second_time_value = format_time_value(second_time_value)
    if second_time_value > first_time_value:
        time_interval_length = (second_time_value - first_time_value).seconds
    else:
        time_interval_length = (first_time_value - second_time_value).seconds
    return time_interval_length


# 获取PC的当前时间，精确到毫秒
def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - long(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp


def get_pixel(image, x, y, G, N):
    l = image.getpixel((x, y))
    if l > G:
        l = True
    else:
        l = False

    near_dots = 0
    if l == (image.getpixel((x - 1, y - 1)) > G):
        near_dots += 1
    if l == (image.getpixel((x - 1, y)) > G):
        near_dots += 1
    if l == (image.getpixel((x - 1, y + 1)) > G):
        near_dots += 1
    if l == (image.getpixel((x, y - 1)) > G):
        near_dots += 1
    if l == (image.getpixel((x, y + 1)) > G):
        near_dots += 1
    if l == (image.getpixel((x + 1, y - 1)) > G):
        near_dots += 1
    if l == (image.getpixel((x + 1, y)) > G):
        near_dots += 1
    if l == (image.getpixel((x + 1, y + 1)) > G):
        near_dots += 1

    if near_dots < N:
        return image.getpixel((x, y-1))
    else:
        return None


def version_cmp(v1, v2):
    l1 = v1.split('.')
    l1 = [int(x) for x in l1]
    l2 = v2.split('.')
    l2 = [int(x) for x in l2]
    if l1[0] > l2[0]:
        return True
    elif l1[0] == l2[0] and l1[1] >= l2[1]:
        return True
    else:
        return False

# CHAOREN_URL = 'http://api2.sz789.net:88'
# CHAOREN_USERNAME = '874820751m'
# CHAOREN_PASSWORD = '874820751m'
# SOFTID = '70135'
#
#
# def distinguish_code(image_file):
#     with open(image_file, 'rb') as f:
#         byte_array = bytearray(f.read())
#         hex_array = []
#         for b in byte_array:
#             hex_string = hex(b)[2:]
#             if len(hex_string) == 1:
#                 hex_string = '0' + hex_string
#             hex_array.append(hex_string)
#         image_string = ''.join(hex_array)
#         res = requests.post(CHAOREN_URL + '/RecvByte.ashx',
#                             data=dict(username=CHAOREN_USERNAME,
#                                       password=CHAOREN_PASSWORD,
#                                       softId=SOFTID,
#                                       imgdata=image_string))
#         ret = json.loads(res.content)
#         print(ret)


PATH = lambda f, p: os.path.abspath(os.path.join(os.path.dirname(f), p))


# if __name__ == '__main__':
#     from Constant import ROOT_DIR
#     distinguish_code(os.path.join(ROOT_DIR, u'captcha.jpg'))

# class ConfigIni:
#     def __init__(self):
#         self.current_directory = os.path.split(
#             os.path.realpath(sys.argv[0]))[0]
#         self.path = os.path.join(ROOT_DIR, 'data', 'test_info.ini')
#         self.cf = ConfigParser.ConfigParser()
#
#         self.cf.read(self.path)
#
#     def get_ini(self, title, value):
#         return self.cf.get(title, value)
#
#     def set_ini(self, title, value, text):
#         self.cf.set(title, value, text)
#         return self.cf.write(open(self.path, "wb"))
#
#     def add_ini(self, title):
#         self.cf.add_section(title)
#         return self.cf.write(open(self.path))
#
#     def get_options(self, data):
#         # 获取所有的section
#         options = self.cf.options(data)
#         return options


# class Asql:
#     def __init__(self, ):
#         ini = ConfigIni()
#         test_db_path = ini.get_ini('test_db', 'test_result')
#         test_db_path = os.path.join(os.path.split(__file__)[0],test_db_path)
#         self.conn = sqlite3.connect(test_db_path)
#         self.cursor = self.conn.cursor()
#         self.__is_table()
#
#     def execute(self, *args, **kwargs):
#         """
#
#         :param args:
#         :param kwargs:
#         :return: 提交数据
#         """
#         self.cursor.execute(*args, **kwargs)
#
#     def close(self):
#         self.cursor.close()
#         self.conn.commit()
#         self.conn.close()
#
#     def __is_table(self):
#         """
#         判断表是否存在
#         :return:
#         """
#         self.cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='test_results'")
#         row = self.cursor.fetchone()
#         if row[0] != 1:
#             self.__built_table()
#
#     def __built_table(self):
#         """
#         建表
#         :return:
#         """
#         self.execute("""
#         CREATE TABLE test_results
#         (
#             case_id INTEGER PRIMARY KEY,
#             case_name TEXT,
#             device_name TEXT,
#             cpu_list TEXT,
#             mem_list TEXT,
#             execution_status TEXT,
#             error_str TEXT,
#             phone_name TEXT,
#             created_time DATETIME DEFAULT (datetime('now', 'localtime'))
#         );""")
#
#     def insert_per(self, case_name, device_name, cpu_list, mem_list, execution_status, error_str, phone_name, ):
#         key = "(case_name,device_name,cpu_list,mem_list,execution_status,error_str,phone_name,created_time)"
#         values = "('{}','{}','{}','{}','{}','{}','{}','{}')" \
#             .format(case_name, device_name, cpu_list, mem_list, execution_status, error_str, phone_name, get_now_time())
#         self.execute("INSERT INTO test_results {} VALUES {}".format(key, values))
#
#     def select_per(self, case_name, device_name):
#         statement = "select * from test_results where " \
#                     "case_name = '{}' " \
#                     "and " \
#                     "device_name = '{}' " \
#                     "and " \
#                     "execution_status = 1 " \
#                     "order by created_time desc".format(case_name, device_name)
#         self.cursor.execute(statement)
#         row = self.cursor.fetchone()
#         if row is not None:
#             cpu = re.findall(r"\d+\.?\d*", row[3])
#             mem = re.findall(r"\d+\.?\d*", row[4])
#             return [int(i) for i in cpu], [int(i) for i in mem]
#         else:
#             return None
