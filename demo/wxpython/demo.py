import wx


class Mywin(wx.Frame):
    def __init__(self, parent, title,*args,**kwargs):
        super(Mywin, self).__init__(parent, title=title,*args,**kwargs)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 数据库连接参数
        db = wx.StaticBox(panel, -1, '数据库连接:')
        dbSizer = wx.StaticBoxSizer(db,wx.VERTICAL)

        dbGrid = wx.GridBagSizer(0, 0)
        dbAddrST = wx.StaticText(panel, -1, "主机地址")
        dbAddrTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT)
        dbPortST = wx.StaticText(panel, -1, "端口")
        dbPortTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT)
        dbNameST = wx.StaticText(panel, -1, "数据库名")
        dbNameTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT)
        dbGrid.Add(dbAddrST, pos=(0, 0), flag=wx.ALL | wx.CENTER, border=5)
        dbGrid.Add(dbAddrTC, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=5)
        dbGrid.Add(dbPortST, pos=(0, 2), flag=wx.ALL | wx.CENTER, border=5)
        dbGrid.Add(dbPortTC, pos=(0, 3), flag=wx.ALL | wx.EXPAND, border=5)
        dbGrid.Add(dbNameST, pos=(1, 0), flag=wx.ALL | wx.CENTER, border=5)
        dbGrid.Add(dbNameTC, pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5)
        dbSizer.Add(dbGrid, 0, wx.ALL | wx.ALIGN_LEFT, 10)

        # 登陆参数
        login = wx.StaticBox(panel, -1, '登录:')
        loginSizer = wx.StaticBoxSizer(login, wx.VERTICAL)

        loginGrid = wx.GridBagSizer(0, 0)
        loginUsrST = wx.StaticText(panel, -1, "用户名")
        loginUsrTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT)
        loginPwdST = wx.StaticText(panel, -1, "密码")
        loginPwdTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT|wx.TE_PASSWORD)
        loginBtn = wx.Button(panel, -1, label="测试连接", style=wx.ALIGN_LEFT|wx.CENTER)
        loginGrid.Add(loginUsrST, pos=(0, 0), flag=wx.ALL | wx.CENTER, border=5)
        loginGrid.Add(loginUsrTC, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=5)
        loginGrid.Add(loginPwdST, pos=(1, 0), flag=wx.ALL | wx.CENTER, border=5)
        loginGrid.Add(loginPwdTC, pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5)
        loginGrid.Add(loginBtn, pos=(2, 1),span=(1,2), flag=wx.ALIGN_RIGHT| wx.CENTER, border=5)
        loginSizer.Add(loginGrid, 0, wx.ALL | wx.ALIGN_LEFT, 10)

        dbSizer.Add(loginSizer, 0, wx.ALL | wx.ALIGN_LEFT, 10)
        vbox.Add(dbSizer, 0, wx.ALL|wx.EXPAND | wx.ALIGN_LEFT, 10)


        # 运行参数
        param = wx.StaticBox(panel, -1, '运行参数:')
        paramSizer = wx.StaticBoxSizer(param, wx.VERTICAL)

        paramGrid = wx.GridBagSizer(0, 0)
        fixValST = wx.StaticText(panel, -1, "设定值")
        fixValTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT)
        offsetST = wx.StaticText(panel, -1, "时间补偿/s")
        offsetTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, value='0')
        tbNameST = wx.StaticText(panel, -1, "表名")
        tbNameTC = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT | wx.TE_MULTILINE)
        paramGrid.Add(fixValST, pos=(0, 0), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(fixValTC, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.Add(offsetST, pos=(0, 2), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(offsetTC, pos=(0, 3), flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.Add(tbNameST, pos=(1, 0), flag=wx.ALL | wx.CENTER, border=5)
        paramGrid.Add(tbNameTC, pos=(1, 1), span=(7,3),flag=wx.ALL | wx.EXPAND, border=5)
        paramGrid.AddGrowableRow(3)
        paramSizer.Add(paramGrid, 0, wx.ALL | wx.ALIGN_LEFT, 10)

        vbox.Add(paramSizer, 0, wx.ALL | wx.ALIGN_LEFT, 10)

        sbox = wx.StaticBox(panel, -1, 'buttons:')
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(panel, -1, 'ok')
        cancelButton = wx.Button(panel, -1, 'cancel')
        hbox.Add(okButton, 0, wx.ALL | wx.LEFT, 10)
        hbox.Add(cancelButton, 0, wx.ALL | wx.LEFT, 10)
        sboxSizer.Add(hbox, 0, wx.ALL | wx.LEFT, 10)

        vbox.Add(sboxSizer, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(vbox)
        self.Centre()

        panel.Fit()
        self.Show()


app = wx.App()
Mywin(None, 'staticboxsizer demo', size=(500,800))
app.MainLoop()
