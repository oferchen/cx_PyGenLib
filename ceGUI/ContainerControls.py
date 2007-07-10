"""
Defines controls that contain other controls with extensions to wx
functionality.
"""

import ceGUI
import wx

__all__ = ["BaseContainer", "Dialog", "Frame", "Panel", "StandardDialog",
           "TopLevelFrame" ]


class BaseContainer(ceGUI.BaseControl):
    saveSize = savePosition = bindClose = True
    minSize = None

    def _Initialize(self):
        if self.minSize is not None:
            self.SetMinSize(self.minSize)
        super(BaseContainer, self)._Initialize()

    def _OnClose(self, event):
        self._SaveSettings()
        self.OnClose()
        event.Skip()

    def _OnCreate(self):
        if self.bindClose:
            self.Bind(wx.EVT_CLOSE, self._OnClose)
        self.OnCreate()
        topSizer = self.OnLayout()
        if topSizer is not None:
            self._OnLayout(topSizer)
        self._RestoreSettings()

    def _OnLayout(self, topSizer):
        self.SetSizer(topSizer)
        if self.minSize is None:
            topSizer.Fit(self)

    def _RestoreSettings(self):
        if self.saveSize:
            size = self.ReadSetting("Size", self.minSize, isComplex = True)
            if size is not None:
                self.SetSize(size)
        if self.savePosition:
            position = self.ReadSetting("Position", isComplex = True)
            if position is not None:
                self.SetPosition(position)
        self.RestoreSettings()

    def _SaveSettings(self):
        if self.saveSize:
            self.WriteSetting("Size", self.GetSizeTuple(), isComplex = True)
        if self.savePosition:
            self.WriteSetting("Position", self.GetPositionTuple(),
                    isComplex = True)
        self.SaveSettings()
        self.settings.Flush()

    def AddButton(self, label, method = None):
        button = wx.Button(self, -1, label)
        if method is not None:
            self.BindEvent(button, wx.EVT_BUTTON, method)
        return button

    def AddChoiceField(self, *choices):
        return wx.Choice(self, choices = choices)

    def AddLabel(self, label = ""):
        return wx.StaticText(self, -1, label)

    def AddTextField(self, readOnly = False):
        if readOnly:
            style = wx.TE_READONLY
        else:
            style = 0
        field = wx.TextCtrl(self, -1, style = style)
        if readOnly:
            color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
            field.SetBackgroundColour(color)
        return field

    def CreateFieldLayout(self, *controls):
        numRows = len(controls) / 2
        sizer = wx.FlexGridSizer(rows = numRows, cols = 2, vgap = 5, hgap = 5)
        sizer.AddGrowableCol(1)
        for index, control in enumerate(controls):
            flag = wx.ALIGN_CENTER_VERTICAL
            if index % 2 == 1:
                flag |= wx.EXPAND
            sizer.Add(control, flag = flag)
        return sizer

    def OnClose(self):
        pass

    def OpenWindow(self, name, *args, **kwargs):
        return ceGUI.OpenWindow(name, self, *args, **kwargs)


class Dialog(BaseContainer, wx.Dialog):
    createOkButton = createCancelButton = True

    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)
        self._Initialize()

    def _OnCreate(self):
        if self.createOkButton:
            self.okButton = wx.Button(self, wx.ID_OK)
            self.BindEvent(self.okButton, wx.EVT_BUTTON, self._OnOk,
                    createBusyCursor = True)
        if self.createCancelButton:
            self.cancelButton = wx.Button(self, wx.ID_CANCEL)
            self.BindEvent(self.cancelButton, wx.EVT_BUTTON, self._OnCancel)
        super(Dialog, self)._OnCreate()

    def _OnOk(self, event):
        self.OnOk()
        self._SaveSettings()

    def _OnCancel(self, event):
        self.OnCancel()
        self._SaveSettings()

    def OnCancel(self):
        pass

    def OnOk(self):
        pass


class Frame(BaseContainer, wx.Frame):
    hasToolbar = hasMenus = True

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self._Initialize()

    def _OnCreate(self):
        if self.hasToolbar:
            self.toolbar = wx.ToolBar(self)
            self.SetToolBar(self.toolbar)
            self.OnCreateToolbar()
            self.toolbar.Realize()
        if self.hasMenus:
            self.menuBar = wx.MenuBar()
            self.SetMenuBar(self.menuBar)
            self.OnCreateMenus()
        super(Frame, self)._OnCreate()

    def AddMenu(self, label):
        menu = wx.Menu()
        self.menuBar.Append(menu, label)
        return menu

    def AddMenuItem(self, menu, label, helpString = "", method = None,
            createBusyCursor = False, radio = False, checkable = False):
        if radio:
            kind = wx.ITEM_RADIO
        elif checkable:
            kind = wx.ITEM_CHECK
        else:
            kind = wx.ITEM_NORMAL
        return self._AddMenuItem(menu, label, helpString, kind, method,
                createBusyCursor)

    def AddStockMenuItem(self, menu, stockId, method = None,
            createBusyCursor = False):
        return self._AddMenuItem(menu, id = stockId, method = method,
                createBusyCursor = createBusyCursor)

    def AddToolbarItem(self, label, bitmapId, shortHelp = "", longHelp = "",
            method = None, createBusyCursor = False):
        bitmap = wx.ArtProvider.GetBitmap(bitmapId, wx.ART_TOOLBAR,
                self.toolbar.GetToolBitmapSize())
        item = self.toolbar.AddLabelTool(-1, label, bitmap,
                shortHelp = shortHelp, longHelp = longHelp)
        if method is not None:
            self.BindEvent(item, wx.EVT_TOOL, method,
                    createBusyCursor = createBusyCursor)
        return item

    def OnCreateToolbar(self):
        pass


class Panel(BaseContainer, wx.Panel):
    saveSize = savePosition = bindClose = False

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._Initialize()


class StandardDialog(Dialog):
    title = ""

    def __init__(self, parent):
        super(StandardDialog, self).__init__(parent, -1, self.title,
                style = wx.CAPTION | wx.RESIZE_BORDER)

    def _OnLayout(self, topSizer):
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.AddStretchSpacer()
        buttonSizer.Add(self.okButton,
                flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 5)
        buttonSizer.Add(self.cancelButton,
                flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 5)
        topSizer.Add(buttonSizer, flag = wx.EXPAND)
        super(StandardDialog, self)._OnLayout(topSizer)


class TopLevelFrame(Frame):
    baseSettingsName = ""

    def OnAbout(self, event):
        dialog = ceGUI.AboutDialog(self)
        dialog.ShowModal()

    def OnEditPreferences(self, event):
        dialog = ceGUI.PreferencesDialog(self)
        dialog.ShowModal()

    def OnExit(self, event):
        self.Close()

