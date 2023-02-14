import logging

import wx
# import wx.lib.inspection

from .model_controller import DataModel, CaptureController
from .utils import get_device_names
from .view import MainWindow


def main():
    # Don't understand why, but call to device.getDevices must be
    # before the wx.App() call.
    devs = get_device_names()

    app = wx.App()
    model = DataModel(
        wx.Colour(0, 0, 0), 1, (0.5, 0.5), True, 2, None,
        0, 15, False, devs
    )
    capture_ctrl = CaptureController(model=model)
    capture_ctrl.start_capture()
    main = MainWindow(None, model, capture_ctrl, title="MicroscoPy-Xhair")
    main.Show()

    # wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()
    capture_ctrl.stop_capture()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
