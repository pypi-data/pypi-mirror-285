# coding=utf-8

"""
error class
"""


class Error(Exception):
    """
        base class for IDDOEMTest error
    """
    pass


class EnvironError(Error):
    """
        base class for environment related error
    """
    pass


class BizError(Error):
    """
        base class for business related error
    """
    pass


class TargetNotFoundError(Error):
    """
        base class for target not found error
    """
    def __init__(self, query):
        self.query = query

    def __str__(self):
        return self.query


class DriverInitError(Error):
    """
        base class for driver init error
    """

    def __init__(self, msg, e=None):
        self.msg = msg
        self.e = e

    def __str__(self):
        if self.e:
            return '{}:{}:Message:{}'.format(self.msg,
                                             self.e.__class__.__name__,
                                             self.e.message or self.e.msg)
        else:
            return self.msg


class DeviceConnectionError(EnvironError):
    """
        base class for device connection error
    """
    DEVICE_CONNECTION_ERROR = r"error:\s*((device \'\S+\' not found)|(cannot connect to daemon at [\w\:\s\.]+ Connection timed out))"

    def __init__(self, serial):
        self.serial = serial

    def __str__(self):
        return '{} connection error'.format(self.serial)


class ScriptParamError(Error):
    """
        base class for script param error
    """
    pass


class PageInitError(Error):
    pass
