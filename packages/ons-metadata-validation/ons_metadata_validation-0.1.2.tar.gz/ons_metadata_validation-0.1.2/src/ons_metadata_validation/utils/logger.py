import logging
import logging.config
import os
from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd
from openpyxl import Workbook


def setup_logger(file: str, idx: int) -> bool:
    """basic setup function

    Args:
        file (str): the dunder method __file__ for the initialising file
        idx (int): the number of folder levels to the logging.ini file

    Returns:
        bool: always True!
    """
    log_folder = get_dir_path(file, idx, "logs")
    os.makedirs(log_folder, exist_ok=True)
    logging.config.fileConfig(
        get_dir_path(file, idx, "logging.ini"),
        defaults={"root": log_folder},
        disable_existing_loggers=False,
    )
    return True


def compress_logging_value(item: type):
    """compresses the larger logging values

    Args:
        item (type): the item for logging

    Returns:
        type: the compressed value for logging (if necessary)
    """
    if isinstance(item, (bool, int, float, str)):
        return item
    if isinstance(item, pd.DataFrame):
        return item.info()
    if isinstance(item, Workbook):
        return f"Workbook.sheetnames: {item.sheetnames}"
    if isinstance(item, (Sequence, Mapping)):
        if len(item) > 10:
            return f"{type(item)}: len({len(item)})"
        return item
    return item


def get_dir_path(src: str, idx: int, dst: str) -> str:
    """converts a local file path to a relative one

    Args:
        src (str): the current location
        idx (int): the number of folder levels to go up or down
        dst (str): the destination location

    Returns:
        str: the file path as a string
    """
    curr_dir = Path(src).parents[idx]
    return str(curr_dir.joinpath(dst)).replace("\\", "/")
