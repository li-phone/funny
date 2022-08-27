from enum import Enum

import wx


def isInt(string, min=float('-inf'), max=float('inf')):
    try:
        num = int(string)
        return min <= num <= max
    except Exception as e:
        return False


def isFloat(string, min=float('-inf'), max=float('inf')):
    try:
        num = float(string)
        return min <= num <= max
    except Exception as e:
        return False


class DataType(Enum):
    def __new__(cls, dtype, desc):
        obj = object.__new__(cls)
        obj.dtype = dtype
        obj.desc = desc
        return obj

    NONE = ('NONE', '无类型')
    DIGIT = ('DIGIT', '数字')
    INT = ('INT', '整数')
    UINT = ('UINT', '正整数')
    NOT_NEG_INT = ('NOT_NEG_INT', '非负整数')
    FLOAT = ('FLOAT', '数值')
    UFLOAT = ('UFLOAT', '正数')
    NOT_NEG_FLOAT = ('NOT_NEG_FLOAT', '非负数')


class NumberValidator(wx.Validator):  # 创建验证器子类
    def __init__(self, dtype=DataType.NONE):
        wx.Validator.__init__(self)
        self.dtype = dtype
        self.ValidInput = '+-.0123456789'
        self.Bind(wx.EVT_CHAR, self.OnCharChanged)  # 绑定字符输入事件
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)  # 绑定字符输入事件

    def OnCharChanged(self, event):
        key = event.GetKeyCode()
        if key == 0:
            return
        if 32 <= key <= 126:
            # 可见字符
            c = chr(key)
            if c not in self.ValidInput:
                return
        event.Skip()

    def OnKillFocus(self, event):
        if self.Validate(None) is True:
            event.Skip()
            return
        self.GetWindow().SetFocus()
        self.GetWindow().SetInsertionPointEnd()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        string = textCtrl.GetValue()
        val_rst = True
        if self.dtype == DataType.DIGIT:
            val_rst = string.isdigit()
        elif self.dtype == DataType.UINT:
            val_rst = isInt(string, 1)
        elif self.dtype == DataType.NOT_NEG_FLOAT:
            val_rst = isFloat(string, 0)
        elif self.dtype == DataType.FLOAT:
            val_rst = isFloat(string)
        if val_rst is False:
            wx.MessageBox(f'请输入{self.dtype.desc}！')
        return val_rst

    def Clone(self):
        return NumberValidator(self.dtype)

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True
