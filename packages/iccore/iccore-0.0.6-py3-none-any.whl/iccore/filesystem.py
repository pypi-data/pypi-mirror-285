import shutil
from pathlib import Path

from .runtime import ctx


def copy(src: Path, dst: Path):
    if ctx.can_modify():
        shutil.copy(src, dst)
    else:
        ctx.add_cmd(f"copy {src} {dst}")


def make_archive(archive_name: Path, format: str, src: Path):
    if ctx.can_modify():
        shutil.make_archive(str(archive_name), format, src)
    else:
        ctx.add_cmd(f"make_archive {archive_name} {format} {src}")


def unpack_archive(src: Path, dst: Path):
    if ctx.can_modify():
        shutil.unpack_archive(src, dst)
    else:
        ctx.add_cmd(f"unpack_archive {src} {dst}")
