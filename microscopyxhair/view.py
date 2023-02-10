import cv2      # TODO Remove this dependency
import wx

from .model_controller import DataModel, CaptureController


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


class CameraPanel(wx.Panel):

    def __init__(self, parent, model: DataModel, cap_ctrl: CaptureController,
                 *args, **kw):
        super().__init__(parent, *args, **kw)

        self.model: DataModel = model
        self.capture_ctrl: CaptureController = cap_ctrl

        self.init_ui()

    def init_ui(self):
        # Following line is *crucial* to avoid flickering!
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        frame = self.get_frame()
        self.init_size(frame)

        self.timer = wx.Timer(self)
        self.timer.Start(int(1000./self.model.framerate))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)

    def init_size(self, frame):
        height, width = frame.shape[:2]
        self.bmp = wx.Bitmap.FromBuffer(width, height, frame)

        self.SetSize((width, height))
        self.SetMinSize((width, height))

    def get_frame(self):
        if not self.model.capture_active:
            raise RuntimeError("Capture not started")
        ret, frame = self.capture_ctrl.capture.read()

        if not ret:
            raise RuntimeError("Cannot get frame")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # N.B. frame.shape returns a tuple: (height, width, color)
        #      - frame is an ndarray
        cv2.line(  # Vertical line
            frame,
            (int(frame.shape[1] * self.model.xhair_centre[0]), 0),
            (int(frame.shape[1] * self.model.xhair_centre[0]), frame.shape[0]),
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )
        cv2.line(  # Horizontal line
            frame,
            (0, int(frame.shape[0] * self.model.xhair_centre[1])),
            (frame.shape[1], int(frame.shape[0] * self.model.xhair_centre[1])),
            color=self.model.xhair_colour,
            thickness=self.model.xhair_thickness
        )
        return frame

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self.bmp)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        if not self.model.capture_active:
            return
        frame = self.get_frame()
        if (
            frame.shape[0] != self.GetSize().GetHeight()
            and frame.shape[1] != self.GetSize().GetWidth()
        ):
            self.init_size(frame)
            wx.PostEvent(self.Parent, wx.EVT_SIZE)

        self.bmp.CopyFromBuffer(frame)
        self.Refresh()

    def OnLeftClick(self, evt: wx.MouseEvent):
        xhair_coord = evt.GetPosition()
        print(f"New crosshair coord: {xhair_coord}")

        new_xhair_centre = tuple(
            xhair_coord[i] / self.GetSize().Get()[i]
            for i in range(2)
        )
        print(f"Converted to new crosshair center: {new_xhair_centre}")
        self.model.xhair_centre = new_xhair_centre

        self.Refresh()


class MainWindow(wx.Frame):

    def __init__(self, parent, model: DataModel, cap_ctrl: CaptureController,
                 *args, **kw):
        super().__init__(
            parent, style=(wx.DEFAULT_FRAME_STYLE
                           & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)),
            *args, **kw)

        self.model: DataModel = model
        self.capture_ctrl = cap_ctrl

        self.init_ui()
        self.Centre()

    def init_ui(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        choose_cam = file_menu.Append(
            wx.ID_ANY, "Active Camera...", "Select active camere"
        )
        xhair_col = file_menu.Append(
            wx.ID_ANY, "Crosshair Color...", "Select crosshair color"
        )
        exit_item = file_menu.Append(wx.ID_EXIT, "Quit", "Quit application")
        menubar.Append(file_menu, "&File")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnChooseCam, choose_cam)
        self.Bind(wx.EVT_MENU, self.OnXhairColour, xhair_col)
        self.Bind(wx.EVT_MENU, self.OnQuit, exit_item)

        bkg_panel = wx.Panel(self)
        bkg_panel.SetBackgroundColour("#4f5049")
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        cam_pan = CameraPanel(bkg_panel, self.model, self.capture_ctrl)
        self.vbox.Add(cam_pan, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        bkg_panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnQuit(self, evt):
        self.capture_ctrl.stop_capture()
        self.Close()

    def OnXhairColour(self, evt):
        new_col = wx.GetColourFromUser(self, self.model.xhair_colour)
        if new_col.IsOk():
            self.model.xhair_colour = new_col

    def OnChooseCam(self, evt):
        current_id = self.model.camera_id
        cam_chooser = CameraIdChooser(self, self.model)
        cam_chooser.ShowModal()
        cam_chooser.Destroy()

        if self.model.camera_id != current_id:
            # Camera has changed, restart the capture
            self.capture_ctrl.stop_capture()
            self.capture_ctrl.start_capture()

    def OnSize(self, evt):
        self.vbox.Fit(self)
