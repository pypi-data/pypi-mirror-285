# -*- coding: utf-8 -*--
import locale
import os
import platform
import re
import shlex
import subprocess
import time
from threading import Timer, Lock

from Utils import kill_by_pid
import error

# 判断系统类型，windows使用findstr，linux使用grep
system = platform.system()
if system is "Windows":
    find_util = "findstr"
else:
    find_util = "grep"


class Adb(object):
    __lock = Lock()
    __serialNum = None
    __process = None
    # default timeout time, we set 20 seconds
    # __timeout may be changed in other place
    __timeout = 40.0
    # default timeout time 20 seconds
    __defaultTimeout = 300.0
    __reTry = 3

    def __init__(self, serialNum=None):
        """
        用于初始化adb，可选参数为device id
        :return:

        """
        self.__serialNum = serialNum

    def get_pid(self,pkg_name):
        output = ""
        # try:
        #     output = self.shell_output('pidof ' + pkg_name)
        # except Exception as msg:
        #     print(msg)
        if output == "":
            output = self.shell_output('ps | grep ' + pkg_name)
            lines = output.splitlines()
            for line in lines:
                keys = line.split()
                if len(keys) > 1 and keys[-1] == pkg_name:
                    return keys[1]
        return output

    def setTimeout(self, timeout):
        """
        设置adb命令超时时间，参数为timeout

        :return:
        :param timeout: 超时时间

        """
        self.__timeout = timeout

    def setDefaultTimeout(self):
        """
        设置adb命令默认超时时间

        :return:

        """
        self.__timeout = self.__defaultTimeout

    def connect(self, ip):
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?$', ip):
            self.adbtimeout("connect " + ip, 10)
        time.sleep(1)

    def disconnect(self, ip):
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?$', ip):
            self.adbtimeout("disconnect " + ip, 10)

    def adbtimeout(self, args, timeout=30):
        """
        执行adb开头的命令

        :return:
        :param args: adb后面接的字符串命令
        :param timeout:
        """
        cmd = 'adb '
        if self.__serialNum:
            cmd += "-s %s " % self.__serialNum
        cmd = ("%s%s" % (cmd, str(args))).encode(locale.getpreferredencoding())
        return self.cmdtimeout(cmd, timeout)

    def cmd_exec_immediately(self,args):
        cmd = 'adb '
        if self.__serialNum:
            cmd += "-s %s " % self.__serialNum
        cmd = ("%s%s" % (cmd, str(args))).encode(locale.getpreferredencoding())
        print cmd
        os.system(cmd)

    def shell_output(self, args):
        cmd = 'adb'
        if self.__serialNum:
            cmd = ' '.join([cmd, '-s', self.__serialNum])
        cmd = ' '.join([cmd, 'shell', args])
        return self.check_output(cmd)

    def shell_open(self, command):
        cmd = ['adb']
        if self.__serialNum:
            cmd.extend(['-s', self.__serialNum])
        cmd.append('shell')
        cmd.extend(shlex.split(command))
        print cmd
        return self.Popen(cmd)

    def shelltimeout(self, args, timeout=30):
        """
        执行adb shell开头的命令

        :return:
        :param args: adb shell后面接的字符串命令
        :param timeout:
        """
        arg = 'shell {}'.format(args)
        return self.adbtimeout(arg, timeout)

    def check_output(self, cmd):
        try:
            output, err, code = self.cmdtimeout(cmd)
            if code != 0:
                str_err = err.decode(locale.getpreferredencoding().encode('utf-8')) if err else u'无'
                raise error.EnvironError(u'命令 "%s"返回非0退出码%d, 错误信息: %s' %
                                         (cmd, code, str_err))
            else:
                return output.strip()
        except error.EnvironError:
            raise
        except Exception:
            raise error.EnvironError(u'命令 "%s"执行超时' % ' '.join(cmd))

    def log_cat(self):
        cmd = ['adb']
        if self.__serialNum:
            cmd.extend(['-s', self.__serialNum])
        cmd.append('logcat')
        cmd.append('-v')
        cmd.append('threadtime')
        return self.Popen(cmd)

    def log_event(self):
        cmd = ['adb']
        if self.__serialNum:
            cmd.extend(['-s', self.__serialNum])
        cmd.append('logcat')
        cmd.append('-b')
        cmd.append('events')
        return self.Popen(cmd)

    def Popen(self, *args, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        self.__lock.acquire()
        p = subprocess.Popen(stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args, **kwargs)
        self.__lock.release()
        return p

    def cmdtimeout(self, args, timeout=30):
        """
        执行命令，并返回命令的输出,有超时可以设置
        :param args:
        :param timeout:
        :return:
        """
        if platform.system() != 'Windows':
            args = shlex.split(args)
        p = self.Popen(args)
        print args

        timer = Timer(timeout, lambda process: kill_by_pid(process.pid), [p])

        try:
            timer.start()
            stdout, stderr = p.communicate()
            return_code = p.returncode
            return stdout, stderr, return_code
        finally:
            timer.cancel()

    def get_android_model(self):
        """
        获取设备中的Android model号，如MiTV4A
        """
        return self.shell_output('getprop ro.product.model').replace(" ","_").replace("\n","").replace("\r","")

    def get_android_version(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        return self.shell_output('getprop ro.build.version.release')

    def get_sdk_version(self):
        """
        获取设备SDK版本号
        """
        return int(self.shell_output('getprop ro.build.version.sdk'))


    # 得到手机信息
    def getPhoneInfo(self):
        # TODO 小米盒子4C的model在报告中错误显示"MiBox4",实际应该"MiBox4C"
        result = {"release": "5.0", "model": "model2", "brand": "brand1", "device": "device1"}
        try:
            release = self.shell_output('getprop ro.build.version.release')  # 版本
            model = self.shell_output('getprop ro.product.model')  # 型号
            brand = self.shell_output('getprop ro.product.brand')  # 品牌
            device = self.shell_output('getprop ro.product.device')  # 设备名
            result["release"] = release
            result["model"] = model
            result["brand"] = brand
            result["device"] = device
        except Exception as e:
            print e
        return result


    def screen_shot(self, appPath):
        """
        获取当前设备的截图,导出到指定目录
        """
        self.shelltimeout("/system/bin/screencap -p /sdcard/temp.png", 10)
        self.pull('/sdcard/temp.png', appPath)
        self.shelltimeout("rm /sdcard/temp.png", 5)


    def touch_by_element(self, element):
        """
        点击元素
        usage: touchByElement(Element().findElementByName(u"计算器"))
        """
        self.shelltimeout("input tap %s %s" % (str(element[0]), str(element[1])), 30)
        time.sleep(0.5)


    def get_focused_package_and_activity(self):
        """
        获取当前应用界面的包名和Activity，返回的字符串格式为：packageName/activityName
        """
        output = self.shell_output('dumpsys window | grep mCurrentFocus')
        output = output.strip().split()
        if output[-1].endswith('}'):
            return output[-1][:-1]
        else:
            return output[-1]

    def get_current_package_name(self):
        """
        获取当前运行的应用的包名
        """
        pkg = self.get_focused_package_and_activity().split("/")
        if len(pkg) > 0:
            return pkg[0]
        else:
            return ''

    def get_current_activity(self):
        """
        获取当前运行应用的activity
        """
        pkg = self.get_focused_package_and_activity().split("/")
        if len(pkg) > 0:
            return pkg[-1]
        else:
            return ''


    def list_dir(self, _dir, find_str=None):
        dirs = self.shell_output('ls ' + _dir)
        if find_str:
            grep_cmd = [find_util, find_str]
            p = self.Popen(grep_cmd, stdin=subprocess.PIPE)
            out, err = p.communicate(dirs)
            return out.strip()
        else:
            return dirs


    def specifies_app_version_name(self, package):
        """
        获取指定应用的versionName
        :param package:应用包名
        :return: 包名,versionName
        """
        versionName = ""
        versionCode = ""
        for package in self.shell_output('dumpsys package %s' % package).splitlines():
            if 'versionName' in package:
                versionName = package.split('=', 2)[1].strip()
            if 'versionCode' in package:
                versionCode = package.split()[0].split('=', 2)[1].strip()
        return versionName + "-" + versionCode

    def get_app_version_name(self, package):
        """
        获取指定应用的versionName
        :param package:应用包名
        :return: 包名
        """
        versionName = ""
        for package in self.shell_output('dumpsys package %s' % package).splitlines():
            if 'versionName' in package:
                versionName = package.split('=', 2)[1].strip()
        return versionName

    # 长按物理按键
    def long_press_key_code(self, key, press_time):
        # 获取aml_keypad对应的event序号
        # result = os.popen("adb shell cat /proc/bus/input/devices")
        model = self.get_android_model()
        res = self.shell_output('cat /proc/bus/input/devices')
        info_line = None
        count = 0
        is_find = False
        for line in res.splitlines():
            if line is "":
                continue
            if is_find:
                count += 1
                if count == 4 and "Handlers=" in line:
                    info_line = line
                    break
                continue
            if "aml_keypad" in line or "NEC_Remote_Controller" in line \
                    or "ff680030.pwm" in line or "XIAOMI Smart TV IR Receiver" in line\
                    or "Hisense Smart TV IR Receiver" in line \
                    or "SKYWORTH_0170" in line or "SONY TV VRC 001" in line \
                    or (model == 'MiBOX4SE' and 'sunxi-ir-uinput' in line)\
                    or (model != 'MiBOX4SE' and model != 'Q5001' and "sunxi-ir" in line):
                is_find = True

        event_info = None
        if info_line is None:
            event_info = "event0"
        else:
            info_line = str(info_line).split("Handlers=")[1]
            info_list = str(info_line).split(" ")
            for temp in info_list:
                if str(temp).startswith("event"):
                    event_info = temp
                    break
        if event_info is None:
            event_info = "event0"

        is_special = False
        if model in ['DYOS', 'MiBOX4SE']:
            is_special = True

        if not is_special:
            long_press_right = '"sendevent /dev/input/%s 1 106 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 106 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_left = '"sendevent /dev/input/%s 1 105 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 105 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_up = '"sendevent /dev/input/%s 1 103 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 103 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_down = '"sendevent /dev/input/%s 1 108 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 108 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_center = '"sendevent /dev/input/%s 1 28 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 28 0 && sendevent /dev/input/%s 0 0 0"'
        else:
            long_press_right = '"sendevent /dev/input/%s 1 22 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 22 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_left = '"sendevent /dev/input/%s 1 21 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 21 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_up = '"sendevent /dev/input/%s 1 19 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 19 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_down = '"sendevent /dev/input/%s 1 20 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 20 0 && sendevent /dev/input/%s 0 0 0"'
            long_press_center = '"sendevent /dev/input/%s 1 23 1 && sendevent /dev/input/%s 0 0 0 && sleep {} && sendevent /dev/input/%s 1 23 0 && sendevent /dev/input/%s 0 0 0"'

        command = None
        if key == KeyCode.KEYCODE_DPAD_RIGHT:
            command = str(long_press_right) % (event_info, event_info, event_info, event_info)
        elif key == KeyCode.KEYCODE_DPAD_LEFT:
            command = str(long_press_left) % (event_info, event_info, event_info, event_info)
        elif key == KeyCode.KEYCODE_DPAD_UP:
            command = str(long_press_up) % (event_info, event_info, event_info, event_info)
        elif key == KeyCode.KEYCODE_DPAD_DOWN:
            command = str(long_press_down) % (event_info, event_info, event_info, event_info)
        elif key == KeyCode.KEYCODE_DPAD_CENTER:
            command = str(long_press_center) % (event_info, event_info, event_info, event_info)

        if command is not None:
            self.shelltimeout(command.format(press_time), press_time + 5)
        else:
            raise Exception(u"无此长按指令，请检查")

    def send_key_event(self, keycode):
        """
        发送一个按键事件
        args:
        - keycode -:
        http://developer.android.com/reference/android/view/KeyEvent.html
        usage: sendKeyEvent(keycode.HOME)
        """
        self.shelltimeout("input keyevent %s" % str(keycode), 5)
        time.sleep(0.5)


    def __mem_mem_total(self):
        output = self.shell_output('cat proc/meminfo')
        while True:
            r = output.strip().decode('utf-8')
            if r and 'MemTotal' in r:
                lst = [MemTotal for MemTotal in r.split(' ') if MemTotal]
                return int(lst[1])


    def devices(self):
        cmd = 'adb'
        cmd = ' '.join([cmd, 'devices'])
        return self.check_output(cmd).splitlines()


    def install(self, appPath):
        if not os.path.exists(appPath):
            print('the app path %s does not exists!' % appPath)
        # self.execCmd('install -r %s' % appPath)
        self.adbtimeout('install -r %s' % appPath)

    def installWithOutput(self, appPath, saveFile):
        if not os.path.exists(appPath):
            print('the app path %s does not exists!' % appPath)
        # (stdout, stderr, return_code) = self.adbtimeout('install -r "%s" > "%s" 2>&1' % (appPath, saveFile), int(self.__timeout))
        (stdout, stderr, return_code) = self.adbtimeout('install -r "%s"' % appPath, int(self.__timeout))
        with open(saveFile, "a") as f:
            f.write(stdout)
            f.write(stderr)
            f.write(str(return_code))
        self.__timeout = self.__defaultTimeout
        return return_code

    def uninstall(self, package):
        if package != '':
            self.adbtimeout('uninstall %s' % package, int(self.__timeout))

    def uninstallWithOutput(self, package, saveFile):
        return self.adbtimeout('uninstall %s | tee %s 2>&1' % (package, saveFile), 5)

    def pull(self, devPath, localPath):
        return self.adbtimeout('pull %s %s' % (devPath, localPath), 120)

    def pullSync(self, devPath, localPath):
        self.cmd_exec_immediately('pull %s %s' % (devPath, localPath))

    def push(self, local_path, dev_path):
        self.adbtimeout('push %s %s' % (local_path, dev_path))

    def start_uiautomator(self, app_name):
        self.shelltimeout('uiautomator runtest AppiumBootstrap.jar -c '
                   'io.appium.android.bootstrap.Bootstrap -e pkg %s -e '
                   'disableAndroidWatchers false -e acceptSslCerts false' % app_name, 10)

    def amStartApp(self, appname, mainactivity):
        self.shelltimeout('am start -n %s/%s' % (appname, mainactivity), 10)

    def amStartApp2File(self, appname, mainactivity, saveFile):
        self.shelltimeout('am start -n %s/%s >> %s 2>&1' % (appname, mainactivity, saveFile))

    # only above android 4.0 support this function
    def amStopApp(self, appname):
        self.shelltimeout('am force-stop %s' % appname, 10)

    def inputKeyEvent(self, key):
        self.shelltimeout('input keyevent %s' % key, 5)

    def inputKeyEventImmediately(self, key):
        self.cmd_exec_immediately(' shell input keyevent %s' % key)


    def getDeviceStatus(self, isInStability=False):
        status = ''
        result = self.devices()
        for line in result:
            line = line.strip()
            items = line.split()
            if len(items) == 2:
                if self.__serialNum is not None and items[0] == self.__serialNum:
                    status = items[1]
                    break
                elif self.__serialNum is None:
                    status = items[1]
                    break
        return status

    def getAdbStatus(self):
        try:
            status = self.getDeviceStatus(True)
            if status != '':
                if status == 'device':
                    lines = self.shell_output('echo hello').splitlines()
                    out = lines[0].strip().decode('utf-8')
                    if "error: closed" in out:
                        print("Auto Skip test: %s error: closed" % self.__serialNum)
                        return 'error'
                    elif 'hello' in out:
                        return 'online'
                    else:
                        return 'exception'
                elif status == 'offline':
                    print("Auto Skip test: %s offline" % self.__serialNum)
                    return 'offline'
                else:
                    print("Auto Skip test: %s adb exception" % self.__serialNum)
                    return 'exception'
            else:
                print("Auto Skip test: %s device not found" % self.__serialNum)
                return 'disconnected'
        except Exception as ex:
            print(ex)
            return 'exception'


    def killTop(self):
        topPid = -1
        print("kill the top process in phone")
        processinfo = self.shell_output('ps').splitlines()
        for line in processinfo:
            line = line.strip()
            items = line.split()
            if items[-1] == 'top':
                topPid = items[1]
                self.shelltimeout('kill %s' % topPid)
                break

    def stopApp(self, appname):
        pid = -1
        processinfo = self.shell_output('ps').splitlines()
        for line in processinfo:
            line = line.strip()
            items = line.split()
            if items[-1] == appname:
                pid = items[1]
                self.shelltimeout('kill -9 %s' % pid)
                break

    def send_text(self, string):
        """
        发送一段文本，只能包含英文字符和空格，多个空格视为一个空格
        usage: sendText("i am unique")
        """
        text = str(string).split(" ")
        out = []
        for i in text:
            if i != "":
                out.append(i)
        length = len(out)
        for i in range(length):
            self.shelltimeout("input text %s" % out[i], 5)
        time.sleep(0.5)


#  Keycode 键盘输入的公共类  主要是大家可以直接从类里面查阅需要输入的keycode值是多少
class KeyCode:
    """按键Home 3"""
    KEYCODE_HOME = 3
    '''菜单键 82'''
    KEYCODE_MENU = 82
    '''返回键 4'''
    KEYCODE_BACK = 4
    '''搜索键 84'''
    KEYCODE_SEARCH = 84
    '''电源键 26'''
    KEYCODE_POWER = 26
    '''回车键 66'''
    KEYCODE_ENTER = 66
    '''ESC 键 111'''
    KEYCODE_ESCAPE = 111
    '''导航键 确定键 23'''
    KEYCODE_DPAD_CENTER = 23
    '''导航键 向上 19'''
    KEYCODE_DPAD_UP = 19
    '''导航键 向下 20'''
    KEYCODE_DPAD_DOWN = 20
    '''导航键 向左 21'''
    KEYCODE_DPAD_LEFT = 21
    '''导航键 向右 22'''
    KEYCODE_DPAD_RIGHT = 22
    '''向上翻页键 92'''
    KEYCODE_PAGE_UP = 92
    '''向下翻页键 93'''
    KEYCODE_PAGE_DOWN = 93
    '''退格键 67'''
    KEYCODE_DEL = 67
    '''删除键 112'''
    KEYCODE_FORWARD_DEL = 112
    '''插入键 124'''
    KEYCODE_INSERT = 124
    '''Tab 键 61'''
    KEYCODE_TAB = 61
    '''小键盘锁 143'''
    KEYCODE_NUM_LOCK = 143
    '''大写锁定键 115'''
    KEYCODE_CAPS_LOCK = 115
    '''输入0-9的数字'''
    KEYCODE_NUM_0 = 7
    KEYCODE_NUM_1 = 8
    KEYCODE_NUM_2 = 9
    KEYCODE_NUM_3 = 10
    KEYCODE_NUM_4 = 11
    KEYCODE_NUM_5 = 12
    KEYCODE_NUM_6 = 13
    KEYCODE_NUM_7 = 14
    KEYCODE_NUM_8 = 15
    KEYCODE_NUM_9 = 16
    '''输入A-Z的英文字母'''
    KEYCODE_A = 29
    KEYCODE_B = 30
    KEYCODE_C = 31
    KEYCODE_D = 32
    KEYCODE_E = 3
    KEYCODE_F = 34
    KEYCODE_G = 35
    KEYCODE_H = 36
    KEYCODE_I = 37
    KEYCODE_J = 38
    KEYCODE_K = 39
    KEYCODE_L = 40
    KEYCODE_M = 41
    KEYCODE_N = 42
    KEYCODE_O = 43
    KEYCODE_P = 44
    KEYCODE_Q = 45
    KEYCODE_R = 46
    KEYCODE_S = 47
    KEYCODE_T = 48
    KEYCODE_U = 49
    KEYCODE_V = 50
    KEYCODE_W = 51
    KEYCODE_X = 52
    KEYCODE_Y = 53
    KEYCODE_Z = 54

if __name__ == "__main__":
    myAdb = Adb('192.168.199.149:5555')