# MicroscoPy-Xhair
MicroscoPy-xhair is a simple USB microscope viewer, written in Python, which adds a configurable crosshair to the camera image.

MicroscoPy-xhair is designed for use with USB camera microscopes, but will work with any webcam. Camera images are obtained using [OpenCV](https://opencv.org/) / [opencv-python](https://github.com/opencv/opencv-python). OpenCV is also used to add the crosshairs and additional lines to the images in the user interface. The user interface is created with the python package of the [wx Widgets](https://www.wxwidgets.org/) library, [wxPython](https://www.wxpython.org/).

## Device Enumeration
In systems with multiple webcams/USB cameras connected, OpenCV will recognise multiple devices. Unfortunately it only provides an index to identify the different cameras. The name of the camera is available through DirectShow. The [python-capture-device-list](https://github.com/yushulx/python-capture-device-list) library provides a way to make this name available in python. The library is included as a submodule of this project in the [submodules](./submodules) directory, and a wheel for python 3.10 is included in the project.

## wxPython Installation

### Linux
wxpython wheels are available and can be installed with the command:
pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxpython

### Windows
There is not always an official pre-built wheel available for wxPython. A suitable alternative can be found here:
https://dev.azure.com/oleksis/wxPython/_build/results?buildId=88&view=artifacts&pathAsName=false&type=publishedArtifacts
(for Win x64)
