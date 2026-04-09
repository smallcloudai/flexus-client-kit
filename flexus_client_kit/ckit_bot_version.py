from pathlib import Path


def version_file_path(caller_file: str) -> Path:
    vf = Path(caller_file).resolve().parent.parent / "VERSION"
    if vf.exists():
        return vf
    raise FileNotFoundError("no VERSION file found at %s" % vf)


def read_version_file(caller_file: str) -> str:
    return version_file_path(caller_file).read_text().strip()


def bot_name_from_file(caller_file: str) -> str:
    return Path(caller_file).resolve().parent.name
