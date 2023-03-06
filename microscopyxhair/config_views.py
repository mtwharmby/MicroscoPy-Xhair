import wx

from .model_controller import DataModel


class CameraIdChooser(wx.Dialog):

    def __init__(self, parent, model: DataModel, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.model = model

        self.init_ui()
        self.SetTitle("Select Active Camera")

    def init_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        cams = self.model.available_cameras

        combo_label = wx.StaticText(self, label="Select USB camera:")
        self.combo = wx.ComboBox(
            self, value=cams[self.model.camera_id], choices=cams
        )

        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, label="OK")
        cancel_btn = wx.Button(self, label="Cancel")
        btn_box.Add(ok_btn)
        btn_box.Add(cancel_btn, flag=wx.LEFT, border=5)

        ok_btn.Bind(wx.EVT_BUTTON, self.OnOk)
        cancel_btn.Bind(wx.EVT_BUTTON, self.OnCancel)

        vbox.Add(combo_label, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        vbox.Add(self.combo, flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT,
                 border=10)
        vbox.Add(btn_box, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.SetSizer(vbox)
        vbox.Fit(self)

    def OnOk(self, evt):
        cam_id = self.combo.GetSelection()
        if cam_id != wx.NOT_FOUND:
            # A selection has been made by the user, update the camer
            self.model.camera_id = cam_id

        self.Destroy()

    def OnCancel(self, evt):
        self.Destroy()
