import logging

import wx

from .model_controller import (DataModel, CaptureController,
                               CrosshairController)


class CameraPanel(wx.Panel):

    def __init__(self, parent, model: DataModel, cap_ctrl: CaptureController,
                 *args, **kw):
        super().__init__(parent, *args, **kw)
        self.logger = logging.getLogger(__name__)

        self.model: DataModel = model
        self.capture_ctrl: CaptureController = cap_ctrl
        self.xhair_ctrl: CrosshairController = CrosshairController(self.model)

        self.init_ui()

    def init_ui(self) -> None:
        # Following line is *crucial* to avoid flickering!
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        frame = self.get_frame()
        self.init_size(frame)

        self.timer = wx.Timer(self)
        self.timer.Start(int(1000./self.model.framerate))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

        # For mouse events see: https://docs.wxpython.org/wx.MouseEvent.html
        self.Bind(wx.EVT_RIGHT_DCLICK, self.RecenterByClick)

    def init_size(self, frame) -> None:
        height, width = frame.shape[:2]
        self.bmp = wx.Bitmap.FromBuffer(width, height, frame)

        self.SetSize((width, height))
        self.SetMinSize((width, height))
        self.logger.debug(f"Camera frame size changed to: {(width, height)}")

    def get_frame(self) -> None:
        if not self.model.capture_active:
            raise RuntimeError("Capture not started")
        ret, frame = self.capture_ctrl.capture.read()

        if not ret:
            raise RuntimeError("Cannot get frame")

        return self.xhair_ctrl.draw_crosshair(frame)

    def OnPaint(self, evt) -> None:
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

    def RecenterByClick(self, evt: wx.MouseEvent):
        self.xhair_ctrl.recentre_crosshair(
            evt.GetPosition(), self.GetSize().Get()
        )

        self.Refresh()
