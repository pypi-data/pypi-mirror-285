from typing import Dict, List

import pandas as pd

from ons_metadata_validation.processing.developing import (
    md_values_to_df,
)


def get_df_all_fails(fails_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """combines all fails into a dataframe with fail_type for easy indexing

    Args:
        fails_dict (Dict[str, pd.DataFrame]): fail_dict the same format as the
            output from processing.main_process()

    Returns:
        pd.DataFrame: concatenated dataframe of all fails with fail_type col
    """
    dfs: List[pd.DataFrame] = []

    for fail_type, data in fails_dict.items():
        df = pd.DataFrame(split_fail_records(data))
        df["fail_type"] = fail_type
        dfs.append(df)

    return pd.concat(dfs).reset_index(drop=True)


def split_fail_records(df: pd.DataFrame) -> List[Dict]:
    """split fails to one record per reference

    Args:
        df (pd.DataFrame): a fail dataframe

    Returns:
        List[Dict]: the list of dictionary object with one fail per ref
    """
    records = df.to_dict("records")

    split_records = []

    for record in records:
        for ref in record["cell_refs"].split(", "):
            # to [:-1] as always an empty string because reason ends with ". "
            for reason in record["reason"].split(". ")[:-1]:
                split_records.append(
                    {
                        "tab": record["tab"],
                        "name": record["name"],
                        "value": record["value"],
                        "reason": f"{reason}. ",
                        "cell_refs": ref,
                    }
                )
    return split_records


def get_tab_lens(metadata_values) -> Dict[str, int]:
    tabs = [
        "Dataset Resource",
        "Dataset File",
        "Dataset Series",
        "Variables",
        "Codes and Values",
    ]

    df_dict = {tab: md_values_to_df(metadata_values, tab) for tab in tabs}
    return {tab: len(df_dict[tab]) for tab in tabs}
