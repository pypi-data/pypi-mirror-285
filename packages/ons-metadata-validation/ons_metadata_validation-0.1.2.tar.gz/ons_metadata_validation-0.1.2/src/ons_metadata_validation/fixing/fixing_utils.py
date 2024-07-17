import logging
from datetime import datetime
from typing import Dict, List

import pandas as pd
from openpyxl import Workbook
from tqdm import tqdm

import ons_metadata_validation.fixing.string_fixes as sf
from ons_metadata_validation.utils.logger import (
    compress_logging_value,
)

logger = logging.getLogger()


FIX_FUNCTIONS = {
    "must_not_start_with_whitespace": sf.remove_whitespace,
    "must_not_end_with_whitespace": sf.remove_whitespace,
    "must_end_with_a_full_stop_or_question_mark": sf.add_full_stop,
    "must_not_contain_double_spaces": sf.remove_multiple_spaces,
    "must_be_alphanumeric_only": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_spaces": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_underscores": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_spaces_or_underscores": sf.replace_non_breaking_space,
    "must_be_alphanumeric_with_dashes": sf.replace_non_breaking_space,
}


def fix_main(wb: Workbook, fails_dict: Dict[str, pd.DataFrame], filename: str):
    """main function for fixing metadata issues

    Args:
        wb (Workbook): the workbook to be modified (passed by reference)
        fails_dict (Dict[str, pd.DataFrame]): hard and soft fail dfs in a dict
        filename (str): the original filename of the metadata
    """
    for key, val in locals().items():
        logger.debug(f"{key} = {compress_logging_value(val)}")

    for fail_type, fail_df in tqdm(
        fails_dict.items(), "fixing possible hard and soft fails"
    ):
        fails = fail_df.to_dict("records")
        fix_fails(wb, fails)

    validation_datetime = datetime.now().strftime("%Y%m%d_%H%M")
    wb.save(filename.replace(".xlsx", f"_FIXED_{validation_datetime}.xlsx"))


def fix_fails(wb: Workbook, fails: List[Dict]) -> bool:
    """wrapper function that loops over all fails. Calls fix_fail for all
    fails in list

    Args:
        wb (Workbook): the workbook to be modified (passed by reference)
        fails (List[Dict]): list of dicts one dict per fail

    Returns:
        bool: True if all fix_fails are True
    """

    if len(fails) == 0:
        return True

    successes = []

    for fail in fails:
        if isinstance(fail, dict):
            successes.append(fix_fail(wb, fail))

    return all(successes)


def fix_fail(wb: Workbook, fail: dict) -> bool:
    """fixes a single fail, modifies workbook in place

    Args:
        wb (Workbook): the workbook to be modified (passed by reference)
        fail (dict): a dict with fail

    Returns:
        bool: True if all refs are corrected for listed reasons
    """
    successes = []

    reasons = fail["reason"].split(". ")
    refs = fail["cell_refs"].split(", ")

    for reason in reasons:
        for ref in refs:
            if reason not in FIX_FUNCTIONS or ref == "":
                continue
            try:
                wb[fail["tab"]][ref] = FIX_FUNCTIONS[reason](fail["value"])
                successes.append(True)
            except Exception as e:
                logger.error(e)
                successes.append(False)

    return all(successes)
