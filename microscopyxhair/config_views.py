import logging
from typing import Callable

import wx

from .model_controller import DataModel, reset_crosshair_formatting


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


# Event IDs for CrosshairConfig
ID_XH_THICK_SLIDE = wx.NewId()
ID_XH_NR_HGRADS = wx.NewId()


class CrosshairConfig(wx.Dialog):

    """
    xhair_colour: Colour  wx.Colour(0, 0, 0)
    xhair_thickness: int 1
    xhair_hgrads: bool True
    xhair_hgrad_n: int 2
    xhair_hgrads_fixed_sep: int None

    """

    def __init__(self, parent, model: DataModel, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.logger = logging.getLogger(__name__)

        self.model = model
        self.dynamic_widgets: dict[str, EnableHandler] = {}

        self.init_ui()
        self.SetTitle("Configure Crosshair")

    def init_ui(self):
        # TODO Document
        # TODO Cleanup layout
        # TODO Initial placement not on top of main window?
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Line colour controls
        colour_hbox = wx.BoxSizer(wx.HORIZONTAL)
        colour_label = wx.StaticText(self, label="Colour:")
        colour_button = wx.Button(self, label="Select")
        colour_hbox.Add(colour_label, flag=wx.ALIGN_CENTER_VERTICAL)
        colour_hbox.Add(colour_button,
                        flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
        colour_button.Bind(wx.EVT_BUTTON, self.ChooseColour)

        vbox.Add(colour_hbox, flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT,
                 border=10)

        # Line thickness controls
        thick_label = wx.StaticText(self, label="Thickness:")
        thick_slider = SliderWithValue(self, self.model.xhair_thickness, 1, 5)
        self.Bind(
            wx.EVT_SCROLL, self.UpdateThickness, id=thick_slider.SliderId
        )

        vbox.Add(thick_label, flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT,
                 border=10)
        vbox.Add(thick_slider, flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT,
                 border=10)

        # Controls of the horizontal gradations:
        hgrads_sbox = wx.StaticBox(self,
                                   label="Horizontal Gradations:")
        hgrads_sbs = wx.StaticBoxSizer(hgrads_sbox, orient=wx.VERTICAL)

        self.hgrad_cb_id = wx.NewId()
        hgrad_on_check = wx.CheckBox(
            hgrads_sbox, id=self.hgrad_cb_id, label="Show"
        )
        hgrad_on_check.SetValue(self.model.xhair_hgrads)
        self.Bind(wx.EVT_CHECKBOX, self.UpdateHGrads, id=self.hgrad_cb_id)

        n_hgrads_label = wx.StaticText(hgrads_sbox,
                                       label="Number of gradations:")
        n_hgrads_slider = SliderWithValue(
            hgrads_sbox, self.model.xhair_hgrad_n, 1, 5
        )
        # Sets initial enable/disable state of the widget
        # (important unless we call the EnableHandler explicitly)
        n_hgrads_slider.Enable(hgrad_on_check.IsChecked())
        self.Bind(
            wx.EVT_SCROLL, self.UpdateNumHGrads, id=n_hgrads_slider.SliderId
        )

        hgrad_enabler = EnableHandler(
            hgrad_on_check.IsChecked, [n_hgrads_slider,]
        )
        self.dynamic_widgets["xhair_hgrads"] = hgrad_enabler

        hgrads_sbs.Add(hgrad_on_check, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        hgrads_sbs.Add(
            n_hgrads_label, flag=wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP,
            border=10
        )
        hgrads_sbs.Add(
            n_hgrads_slider,
            flag=(wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM), border=10
        )

        vbox.Add(hgrads_sbs, flag=wx.EXPAND | wx.ALL, border=10)

        # Button bar
        button_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        close_button = wx.Button(self, label="Close")
        close_button.Bind(wx.EVT_BUTTON, self.OnClose)
        button_bar_sizer.Add(close_button, flag=wx.LEFT | wx.RIGHT, border=10)

        default_button = wx.Button(self, label="Reset")
        default_button.Bind(wx.EVT_BUTTON, self.OnReset)
        button_bar_sizer.Add(default_button, flag=wx.RIGHT, border=10)

        vbox.Add(button_bar_sizer, flag=wx.EXPAND | wx.BOTTOM, border=10)

        # Resizes dialog (self) so that all the elements in vbox fit exactly
        vbox.Fit(self)
        self.SetSizer(vbox)

    def update_model(self, attr_name: str, evt: wx.Event, val=None):
        if not val:
            elem = evt.GetEventObject()
            val = elem.GetValue()
        if getattr(self.model, attr_name) == val:
            # Value has not changed - do nothing
            return
        setattr(self.model, attr_name, val)
        self.model.force_redraw = True
        self.logger.debug(f"{attr_name} updated to {val}")

    def UpdateThickness(self, evt: wx.ScrollEvent):
        self.update_model("xhair_thickness", evt)

    def UpdateNumHGrads(self, evt: wx.ScrollEvent):
        self.update_model("xhair_hgrad_n", evt)

    def UpdateHGrads(self, evt: wx.CommandEvent):
        enabler = self.dynamic_widgets["xhair_hgrads"]
        enabler.handle_enable()

        self.update_model("xhair_hgrads", evt)

    def ChooseColour(self, evt):
        new_col = wx.GetColourFromUser(self, self.model.xhair_colour)
        if new_col.IsOk():
            self.update_model("xhair_colour", evt, val=new_col)

    def OnReset(self, evt):
        reset_crosshair_formatting(self.model)

    def OnClose(self, evt):
        self.Close()


class SliderWithValue(wx.Panel):

    def __init__(self, parent, value, valMin, valMax, valMap={}, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.slider_id = wx.NewId()
        self.value_map = valMap

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        slider = wx.Slider(
            self, id=self.slider_id,
            value=value, minValue=valMin, maxValue=valMax
        )
        self.slider_value = wx.StaticText(self, label=f"{value}")

        self.Bind(wx.EVT_SCROLL, self.OnScroll, id=self.slider_id)

        hbox.Add(slider, flag=wx.ALIGN_CENTER_VERTICAL)
        hbox.Add(
            self.slider_value, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            border=10
        )

        self.SetSizer(hbox)

    def OnScroll(self, evt: wx.ScrollEvent):
        if evt.GetId() == self.slider_id:
            elem = evt.GetEventObject()
            val = elem.GetValue()
            if self.value_map and val in self.value_map:
                self.slider_value.SetLabel(f"{self.value_map[val]}")
            else:
                self.slider_value.SetLabel(f"{val}")

        # Do not consume the event, propagate onwards
        evt.Skip()

    @property
    def SliderId(self):
        return self.slider_id


class EnableHandler:

    def __init__(
            self, controller: Callable[[], bool], dependents: list[wx.Panel]
    ) -> None:
        self.controller = controller
        self.dependents = dependents

    @property
    def is_enabled(self) -> bool:
        return self.controller()

    def handle_enable(self) -> None:
        for wdgt in self.dependents:
            wdgt.Enable(self.is_enabled)
