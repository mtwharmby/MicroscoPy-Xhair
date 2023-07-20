from pathlib import Path
import shutil
import zipfile

import PyInstaller.__main__


REPO_ROOT = Path(".").resolve()
DIST_PATH = REPO_ROOT / "dist"
REDIST_PATH = REPO_ROOT / "redist"


def run_pyi(root: Path, spec_file: str):
    spec_path = root / spec_file
    if not spec_path.exists():
        raise FileNotFoundError(
            f"Cannot find {spec_file} file. Cannot continue."
        )
    PyInstaller.__main__.run([str(spec_path)])


def zip_dir(dir: Path, zip_file: zipfile.ZipFile, pre_dirs: int = 0):
    for fsobj in dir.iterdir():
        print(fsobj)  # TODO Logging!
        if fsobj.is_dir():
            zip_dir(fsobj, zip_file, pre_dirs)
        else:
            zip_file.write(fsobj, arcname=Path(*fsobj.parts[pre_dirs:]))


def make_zip_dist(zipfile_path: Path):
    # pre_dirs determines number of parent directories to remove from the path
    # Subtract 1 so that we still have a root in the tree
    pre_dirs = len(zipfile_path.parts) - 1
    with zipfile.ZipFile(
        f"{zipfile_path}.zip", "w", zipfile.ZIP_DEFLATED
    ) as zf:
        zip_dir(zipfile_path, zf, pre_dirs=pre_dirs)


def main():
    spec_files = [
        "MicroscoPyXhair_onedir.spec",
        "MicroscoPyXhair_onefile.spec"
    ]

    mpx_dist_path = DIST_PATH / "MicroscoPyXhair"
    if mpx_dist_path.exists():
        shutil.rmtree(mpx_dist_path)

    for sf in spec_files:
        run_pyi(REPO_ROOT, sf)

    make_zip_dist(mpx_dist_path)


def copy_to_redist():
    """
    Create a redist directory and copy the artifacts of the build into it
    """
    # TODO Add a argparse function to allow this to be run by user
    REDIST_PATH.mkdir(exist_ok=True)
    shutil.copy2(
        DIST_PATH / "MicroscoPyXhair.zip",
        REDIST_PATH / "MicroscoPyXhair.zip"
    )
    shutil.copy2(
        DIST_PATH / "MicroscoPyXhair.exe",
        REDIST_PATH / "MicroscoPyXhair.exe"
    )


if __name__ == "__main__":
    main()
