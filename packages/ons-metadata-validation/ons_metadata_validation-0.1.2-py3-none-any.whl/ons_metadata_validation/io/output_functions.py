import logging
from typing import Dict

import pandas as pd

from ons_metadata_validation.utils.logger import (
    compress_logging_value,
)

logger = logging.getLogger()


def save_xlsx(filename: str, data_dict: Dict[str, pd.DataFrame]) -> bool:
    """basic save_xlsx function to save the output report. Does not keep
    excel formatting so should not be used for the wb themselves.

    Args:
        filename (str): the path to save the xlsx at
        data_dict (Dict[str, pd.DataFrame]): the data to save as xlsx

    Returns:
        bool: True if success
    """
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")
    try:
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"File saved successfully at: {filename}")
        return True
    except Exception as e:
        print(f"{e} for {filename}")
        return False
