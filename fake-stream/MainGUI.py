"""
v 2.0.0: 1. 更新为图形化界面
         2. 添加多线程功能点
         3. 添加验证器
         4. 添加用户数据保存和恢复
"""
import hashlib
import os.path

import wx

from FakeStream import connect, FakeStreamWorker, read_bin, write_bin
from NumberValidator import NumberValidator, DataType
from db_utils import strftime


class HomePage(wx.Frame):

    def __init__(self, parent, title, size, *args, **kwargs):
        super(HomePage, self).__init__(parent, title=title, size=size, *args, **kwargs)
        self.SetMaxSize(size)
        self.InitUI()
        self.Centre()
        self.Show()

        self.connection = None
        self.parallel = FakeStreamWorker(is_join=False, print_process=False, logTC=self.logTC)
        self.ctrlNames = (
            'dbAddrTC', 'dbPortTC', 'dbNameTC', 'loginUsrTC', 'loginPwdTC',
            'fixValTC', 'offsetTC', 'speedsTC', 'workerTC', 'tbNameTC',
        )
        self.parameter_path = os.path.join(os.path.expanduser('~'), '.fakestream/.cltr.par')
        self.parameters = read_bin(self.parameter_path)
        self.parameters = {} if self.parameters is None else self.parameters
        self.ReadParameters()

    def ReadParameters(self):
        try:
            if len(self.parameters) == 0 or not isinstance(self.parameters, dict):
                return
            sorted_params = sorted(self.parameters.items(), key=lambda d: d[1]['time'], reverse=True)
            key = sorted_params[0][0]
            parameter = self.parameters.get(key)['data']
            for k, v in parameter.items():
                TC = self.__getattribute__(k)
                if TC is not None:
                    TC.SetValue(v)
        except Exception as e:
            return None

    def SaveParameters(self):
        try:
            parameter = {}
            for name in self.ctrlNames:
                TC = self.__getattribute__(name)
                if TC.Validate() is False:
                    return False
                parameter[name] = TC.GetValue()
            md5_key = hashlib.md5(str(parameter).encode('utf-8')).hexdigest()
            self.parameters[md5_key] = dict(time=strftime(), data=parameter)
            write_bin(self.parameter_path, self.parameters)
            return True
        except Exception as e:
            return True

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        # 数据库连接参数
        db = wx.StaticBox(panel, -1, '数据库配置:')
        dbSizer = wx.StaticBoxSizer(db, wx.VERTICAL)

        dbGrid = wx.GridBagSizer(0, 0)
        self.dbAddrST = wx.StaticText(panel, -1, "主机地址")
        self.dbAddrTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, value='127.0.0.1')
        self.dbPortST = wx.StaticText(panel, -1, "端口")
        self.dbPortTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, value='3306',
                                    validator=NumberValidator(DataType.DIGIT))
        self.dbNameST = wx.StaticText(panel, -1, "数据库名")
        self.dbNameTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT)
        dbGrid.Add(self.dbAddrST, pos=(0, 0), flag=wx.ALL | wx.CENTER, border=5)
        dbGrid.Add(self.dbAddrTC, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=5)
        dbGrid.Add(self.dbPortST, pos=(0, 2), flag=wx.ALL | wx.CENTER, border=5)
        dbGrid.Add(self.dbPortTC, pos=(0, 3), flag=wx.ALL | wx.EXPAND, border=5)
        dbGrid.Add(self.dbNameST, pos=(1, 0), flag=wx.ALL | wx.CENTER, border=5)
        dbGrid.Add(self.dbNameTC, pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5)
        dbSizer.Add(dbGrid, 0, wx.ALL | wx.ALIGN_LEFT, 10)

        # 登陆参数
        login = wx.StaticBox(panel, -1, '登录:')
        loginSizer = wx.StaticBoxSizer(login, wx.VERTICAL)

        loginGrid = wx.GridBagSizer(0, 0)
        self.loginUsrST = wx.StaticText(panel, -1, "用户名")
        self.loginUsrTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT)
        self.loginPwdST = wx.StaticText(panel, -1, "密码")
        self.loginPwdTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT | wx.TE_PASSWORD)
        self.loginBtn = wx.Button(panel, -1, label="测试连接", style=wx.CENTER)
        self.Bind(wx.EVT_BUTTON, self.OnClickConnect, self.loginBtn)
        loginGrid.Add(self.loginUsrST, pos=(0, 0), flag=wx.ALL | wx.CENTER, border=5)
        loginGrid.Add(self.loginUsrTC, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=5)
        loginGrid.Add(self.loginPwdST, pos=(1, 0), flag=wx.ALL | wx.CENTER, border=5)
        loginGrid.Add(self.loginPwdTC, pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5)
        loginGrid.Add(self.loginBtn, pos=(2, 1), span=(1, 1), flag=wx.ALIGN_RIGHT | wx.CENTER, border=5)
        loginSizer.Add(loginGrid, 0, wx.ALL | wx.ALIGN_LEFT, 5)

        dbSizer.Add(loginSizer, 0, wx.ALL | wx.ALIGN_LEFT, 10)
        hbox1.Add(dbSizer, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT, 10)

        # 运行参数
        param = wx.StaticBox(panel, -1, '运行参数:')
        paramSizer = wx.StaticBoxSizer(param, wx.VERTICAL)

        paramGrid = wx.GridBagSizer(0, 0)
        self.fixValST = wx.StaticText(panel, -1, "设定值")
        self.fixValTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, value='6')
        self.offsetST = wx.StaticText(panel, -1, "时间补偿(秒)")
        self.offsetTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, value='0',
                                    validator=NumberValidator(DataType.FLOAT))
        self.workerST = wx.StaticText(panel, -1, "线程数")
        self.workerTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, value='1',
                                    validator=NumberValidator(DataType.UINT))
        self.speedsST = wx.StaticText(panel, -1, "速度(秒/次)")
        self.speedsTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, value='180',
                                    validator=NumberValidator(DataType.NOT_NEG_FLOAT))
        self.tbNameST = wx.StaticText(panel, -1, "表名")
        self.tbNameTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT | wx.TE_MULTILINE)
        paramGrid.Add(self.fixValST, pos=(0, 0), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(self.fixValTC, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.Add(self.offsetST, pos=(0, 2), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(self.offsetTC, pos=(0, 3), flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.Add(self.workerST, pos=(1, 0), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(self.workerTC, pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.Add(self.speedsST, pos=(1, 2), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(self.speedsTC, pos=(1, 3), flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.Add(self.tbNameST, pos=(2, 0), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(self.tbNameTC, pos=(2, 1), span=(5, 3), flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.AddGrowableRow(3)
        paramSizer.Add(paramGrid, 0, wx.ALL | wx.ALIGN_LEFT, 10)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.runBtn = wx.Button(panel, -1, '运行')
        self.stopBtn = wx.Button(panel, -1, '停止')
        self.Bind(wx.EVT_BUTTON, self.OnClickRun, self.runBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.stopBtn)
        btnBox.Add(self.runBtn, 0, wx.ALL | wx.LEFT, 10)
        btnBox.Add(self.stopBtn, 0, wx.ALL | wx.LEFT, 10)
        paramSizer.Add(btnBox, 0, wx.ALL | wx.CENTER, 10)

        hbox1.Add(paramSizer, 0, wx.ALL | wx.ALIGN_LEFT, 10)
        vbox.Add(hbox1, 0, wx.ALL | wx.EXPAND)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        # 运行日志
        log = wx.StaticBox(panel, -1, '运行日志:')
        logSizer = wx.StaticBoxSizer(log, wx.VERTICAL)
        self.logTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT | wx.TE_MULTILINE | wx.HSCROLL)
        logSizer.Add(self.logTC, 1, wx.ALL | wx.EXPAND, border=5)

        hbox2.Add(logSizer, 1, wx.ALL | wx.EXPAND)

        vbox.Add(hbox2, 1, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(vbox)

        panel.Fit()

        self.Bind(wx.EVT_CLOSE, self.OnEvtClose)

    def OnEvtClose(self, event):
        if self.SaveParameters() is True:
            event.Skip()

    def OnClickConnect(self, event):
        addr = self.dbAddrTC.GetValue()
        port = self.dbPortTC.GetValue()
        dbname = self.dbNameTC.GetValue()
        user = self.loginUsrTC.GetValue()
        passwd = self.loginPwdTC.GetValue()
        connect_str = f'{user}@{addr}:{port}/{dbname}'
        if self.connection is None:
            self.connection = connect(connect_str, passwd)
        if self.connection is None:
            wx.MessageBox("连接失败！")
        else:
            wx.MessageBox("连接成功！")

    def OnClickRun(self, event):
        self.OnClickConnect(event)
        run_params = dict(
            fix_val=self.fixValTC.GetValue(),
            time_offset=float(self.offsetTC.GetValue()),
            speed=float(self.speedsTC.GetValue()),
            workers_num=int(self.workerTC.GetValue()),
            table_names=self.tbNameTC.GetValue().split(),
            connection=self.connection,
        )
        self.parallel.update_params(run_params)
        if self.parallel.run_flag is True:
            wx.MessageBox("正在运行！")
            return

        self.parallel.run_flag = True
        self.parallel.parallel = None
        self.parallel()

    def OnClickStop(self, event):
        if self.parallel.run_flag is True:
            self.parallel.run_flag = False
            wx.MessageBox("停止成功！")
        else:
            wx.MessageBox("没有正在运行的程序！")


def main():
    app = wx.App()
    HomePage(None, '数据流工具', size=(810, 600))
    app.MainLoop()


if __name__ == '__main__':
    main()
