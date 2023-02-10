import device

import wx
# import wx.lib.inspection

from .model_controller import DataModel, CaptureController
from .view import MainWindow


def get_devices():


def main():
    # Don't understand why, but call to device.getDevices must be
    # before the wx.App() call.
    devs = get_devices()

    app = wx.App()
    model = DataModel(wx.Colour(0, 0, 0), 1, (0.5, 0.5), 0, 15, False, devs)
    capture_ctrl = CaptureController(model=model)
    capture_ctrl.start_capture()
    main = MainWindow(None, model, capture_ctrl, title="MicroscoPy-Xhair")
    main.Show()

    # wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()


if __name__ == "__main__":
    main()
