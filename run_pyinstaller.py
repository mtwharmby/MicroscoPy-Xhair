from pathlib import Path
import shutil
import PyInstaller.__main__


def run_pyi(root: Path, spec_file: str):
    spec_path = root / spec_file
    if not spec_path.exists():
        raise FileNotFoundError(
            f"Cannot find {spec_file} file. Cannot continue."
        )
    PyInstaller.__main__.run([str(spec_path)])


def main():
    repo_root = Path(".").resolve()
    dist_path = repo_root / "dist"
    redist_path = repo_root / "redist"

    spec_files = [
        "MicroscoPyXhair_onedir.spec",
        "MicroscoPyXhair_onefile.spec"
    ]
    for sf in spec_files:
        run_pyi(repo_root, sf)

    redist_path.mkdir(exist_ok=True)
    shutil.copytree(
        dist_path / "MicroscoPyXhair",
        redist_path / "MicroscoPyXhair"
    )
    shutil.copy2(
        dist_path / "MicroscoPyXhair.exe",
        redist_path / "MicroscoPyXhair.exe"
    )


if __name__ == "__main__":
    main()
