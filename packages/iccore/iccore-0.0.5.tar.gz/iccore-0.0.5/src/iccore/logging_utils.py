import logging


def setup_default_logger(log_filename: str | None = None):
    fmt = "%(asctime)s%(msecs)03d | %(filename)s:%(lineno)s:%(funcName)s | %(message)s"
    logging.basicConfig(
        filename=log_filename,
        filemode="w",
        format=fmt,
        datefmt="%Y%m%dT%H:%M:%S:",
        level=logging.INFO,
    )
