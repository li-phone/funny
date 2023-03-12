import wx


class SelectDialog(wx.Dialog):
    def __init__(self, parent, choices, func_callback=None, title='Select Items', choice_label='Select',
                 size=(300, 130), *args, **kwargs):
        super(SelectDialog, self).__init__(parent, title=title, size=size)
        self.choiceItems = choices
        self.func_callback = func_callback
        self.choiceLabel = choice_label

        self.SetMaxSize(size)
        self.InitUI()

    def InitUI(self):
        # create panel, vbox and hbox
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # create sizer
        sb = wx.StaticBox(panel, -1, self.choiceLabel)
        sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)

        # create Choice
        self.choice = wx.Choice(panel, -1, choices=self.choiceItems)

        sizer.Add(self.choice, 1, wx.ALL | wx.EXPAND | wx.CENTER, border=10)
        hbox.Add(sizer, 1, wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND | wx.CENTER, border=5)

        panel.SetSizer(vbox)

        # bind choice event
        self.choice.Bind(wx.EVT_CHOICE, self.OnChoice)

        self.Centre()
        self.Show()

    def OnChoice(self, event):
        selectIndex = self.choice.GetSelection()
        selectItem = self.choice.GetString(selectIndex)
        if self.func_callback:
            self.func_callback(selectIndex, selectItem)
        self.Destroy()
