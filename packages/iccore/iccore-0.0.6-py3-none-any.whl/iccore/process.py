from pathlib import Path
import subprocess
import os
import logging
import shlex

from .runtime import ctx

logger = logging.getLogger(__name__)


def run(cmd: str, cwd: Path = Path(os.getcwd()), is_read_only: bool = False) -> str:
    """
    This method is intended to be a drop-in for subprocess.run with
    a couple of modifications:

    1) It supports a 'dry run' including a hint on whether
    the command will be 'read only'
    2) It doesn't allow running via a shell, but does convert
    string-like args to a list as needed by execv
    3) It defaults to checking the return code and capturing
    standard out as text
    """

    can_run = ctx.can_modify() or (is_read_only and ctx.can_read())
    if can_run:
        shell_cmd = shlex.split(cmd)
        try:
            result = subprocess.run(
                shell_cmd, check=True, capture_output=True, text=True, cwd=cwd
            )
        except subprocess.CalledProcessError as e:
            msg = f"Error code: {e.returncode} | sterr: {e.stderr}"
            logger.error(msg)
            raise e
        return result.stdout
    else:
        ctx.add_cmd(f"run {cmd}")
        return ""
