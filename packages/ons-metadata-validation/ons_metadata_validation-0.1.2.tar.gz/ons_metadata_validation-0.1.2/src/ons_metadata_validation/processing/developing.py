import logging
from typing import Dict, List

import pandas as pd

from ons_metadata_validation.io import input_functions as inp
from ons_metadata_validation.io.cell_template import (
    MetadataValues,
)
from ons_metadata_validation.utils.logger import (
    compress_logging_value,
)

logger = logging.getLogger()


def md_values_to_df(
    metadata_values: Dict[str, MetadataValues], tab: str
) -> pd.DataFrame:
    """convert a list of metadata values into a pd.DataFrame for a particular tab

    Args:
        metadata_values (List[MetadataValues]): list of populated MetadataValues
        tab (str): the tab to create a pd dataframe for

    Returns:
        pd.DataFrame: the tab values as a dataframe
    """
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")
    values: List = [
        v.values for v in metadata_values.values() if v.cell.tab == tab
    ]
    df = pd.DataFrame(values).T
    df.columns = [
        v.cell.name for v in metadata_values.values() if v.cell.tab == tab
    ]
    return df


def search_md_values(
    metadata_values: Dict[str, MetadataValues], tab: str, name: str
) -> MetadataValues:
    """return metadata values object from {tab} with {name}

    Args:
        metadata_values (List[MetadataValues]): _description_
        tab (str): the tab from the metadata template
        name (str): the name of the column or cell

    Returns:
        MetadataValues: the first item from {tab} with {name}
    """
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")
    key = inp._get_template_dict_key(tab, name)
    if key in metadata_values:
        return metadata_values[key]
    raise NotImplementedError(f"No entry that matches key: {key}")
