from pathlib import Path
import logging

import yaml

from .runtime import ctx

logger = logging.getLogger(__name__)


def read_yaml(path: Path) -> dict:

    if not ctx.can_read():
        ctx.add_cmd(f"read_yaml {path}")
        return {}

    with open(path, encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logging.error("Yaml exception: %s", e)
            raise e
