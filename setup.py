from setuptools import setup, find_packages

setup(
    name="MicrosoPy-Xhair",
    version="1.0.0",
    packages=find_packages(
        include=["microscopy-xhair*"],
        exclude=[]
    ),
    include_package_data=True,
    install_requires=[
        "numpy==1.23.4",
        "opencv-python==4.6.0.66",
        "Pillow==9.3.0",
        "six==1.16.0",
        "windows-capture-device-list @ file:///./submodules/windows_capture_device_list-1.0.1-cp310-cp310-win_amd64.whl",
        "wxPython==4.2.0",
    ],
    entry_points={
        "gui_scripts": [
            "mpyxhair = microscopy-xhair:main",
        ]
    }
)