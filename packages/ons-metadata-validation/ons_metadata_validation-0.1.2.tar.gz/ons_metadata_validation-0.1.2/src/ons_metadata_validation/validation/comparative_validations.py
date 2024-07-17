from typing import Dict, List, Set, Union

import numpy as np
import pandas as pd

from ons_metadata_validation.io.cell_template import MetadataValues
from ons_metadata_validation.processing.developing import (
    md_values_to_df,
    search_md_values,
)
from ons_metadata_validation.reference.lookups import GCP_TYPE_LOOKUP

"""Consistency among stated values"""


def check_DatasetSeries_length_for_DatasetResource_vs_bigquery_table(
    metadata_values: Dict[str, MetadataValues], template_map: Dict
) -> List[Dict]:
    invalid_records = []
    dataset_resource_n_data_series = search_md_values(
        metadata_values,
        template_map["DatasetResource_number_of_dataset_series"]["tab"],
        template_map["DatasetResource_number_of_dataset_series"]["name"],
    )
    dataset_series_gcp_bigquery_table_names = search_md_values(
        metadata_values,
        template_map[
            "DatasetSeries_google_cloud_platform_bigquery_table_name"
        ]["tab"],
        template_map[
            "DatasetSeries_google_cloud_platform_bigquery_table_name"
        ]["name"],
    )

    n_series_count = dataset_resource_n_data_series.values[0]
    dataset_series_count = len(dataset_series_gcp_bigquery_table_names.values)
    if n_series_count != dataset_series_count:
        invalid_records.append(
            {
                "tab": template_map[
                    "DatasetResource_number_of_dataset_series"
                ]["tab"],
                "name": template_map[
                    "DatasetResource_number_of_dataset_series"
                ]["name"],
                "value": n_series_count,
                "reason": "number_of_dataset_series_does_not_match_actual_number_of_series. ",
            }
        )

    return invalid_records


"""Consistency among stated table names"""


def check_table_names_appear_in_main_tabs(
    metadata_values: Dict[str, MetadataValues], template_map: Dict
):
    missing = _check_columns_metadata_match(
        metadata_values,
        [
            template_map[
                "DatasetSeries_google_cloud_platform_bigquery_table_name"
            ]["tab"],
            template_map[
                "DatasetFile_google_cloud_platform_bigquery_table_name"
            ]["tab"],
            template_map[
                "Variables_google_cloud_platform_bigquery_table_name"
            ]["tab"],
        ],
        template_map["Variables_google_cloud_platform_bigquery_table_name"][
            "name"
        ],
    )

    invalid_records = []

    for tab, tables in missing.items():
        for table in tables:
            invalid_records.append(
                {
                    "tab": tab,
                    "name": template_map[
                        "Variables_google_cloud_platform_bigquery_table_name"
                    ]["name"],
                    "value": table,
                    "reason": "table_must_appear_on_DatasetFile_DatasetSeries_and_Variables. ",
                }
            )
    return invalid_records


def _check_columns_metadata_match(
    metadata_values: Dict[str, MetadataValues],
    tab_names: List[str],
    column_name: str,
) -> Dict:
    mvs = []

    for tab in tab_names:
        mvs.append(search_md_values(metadata_values, tab, column_name))

    all_values = _remove_nones_from_set(
        set.union(*[set(mv.values) for mv in mvs])
    )
    missing = {
        mv.cell.tab: sorted(set(mv.values).symmetric_difference(all_values))
        for mv in mvs
    }
    return missing


def _remove_nones_from_set(set: Set):
    return {s for s in set if s != "None"}


"""Consistency among stated variable names"""


def check_Variables_CodesAndValues_is_this_a_code(
    metadata_values: Dict[str, MetadataValues], template_map: Dict
) -> List[Dict]:
    df = md_values_to_df(metadata_values, "Variables")
    codes_and_values_variables = search_md_values(
        metadata_values,
        template_map["CodesandValues_variable_name"]["tab"],
        template_map["CodesandValues_variable_name"]["name"],
    )

    records = df.to_dict("records")
    invalid_records = []

    for record in records:
        if (
            record[template_map["Variables_variable_name"]["name"]]
            in codes_and_values_variables.values
            and record[
                template_map["Variables_is_this_a_code_"]["name"]
            ].lower()
            != "yes"
        ):
            invalid_records.append(
                {
                    "tab": template_map["Variables_is_this_a_code_"]["tab"],
                    "name": template_map["Variables_is_this_a_code_"]["name"],
                    "value": record[
                        template_map["Variables_variable_name"]["name"]
                    ],
                    "reason": "is_this_a_code_must_be_yes_if_on_Codes_and_Values_tab. ",
                }
            )

        if (
            record[template_map["Variables_variable_name"]["name"]]
            not in codes_and_values_variables.values
            and record[
                template_map["Variables_is_this_a_code_"]["name"]
            ].lower()
            == "yes"
        ):
            invalid_records.append(
                {
                    "tab": template_map["CodesandValues_variable_name"]["tab"],
                    "name": template_map["CodesandValues_variable_name"][
                        "name"
                    ],
                    "value": record[
                        template_map["Variables_variable_name"]["name"]
                    ],
                    "reason": "must_appear_on_Codes_and_Values_tab_if_is_this_a_code_is_yes. ",
                }
            )

    return invalid_records


"""Consistency across specific columns"""


def check_Variables_gcp_datatypes(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    records = df.to_dict("records")

    invalid_records = []

    for record in records:
        var_datatype = record[
            template_map["Variables_variable_data_type"]["name"]
        ]
        gcp_datatype = record[template_map["Variables_gcp_data_type"]["name"]]

        if var_datatype.upper() not in GCP_TYPE_LOOKUP:
            invalid_records.append(
                {
                    "tab": template_map["Variables_variable_data_type"]["tab"],
                    "name": template_map["Variables_variable_data_type"][
                        "name"
                    ],
                    "value": var_datatype,
                    "reason": "variable_datatype_not_supported_by_GCP. ",
                }
            )

        elif gcp_datatype != GCP_TYPE_LOOKUP[var_datatype.upper()]:
            invalid_records.append(
                {
                    "tab": template_map["Variables_gcp_data_type"]["tab"],
                    "name": template_map["Variables_gcp_data_type"]["name"],
                    "value": gcp_datatype,
                    "reason": "must_match_valid_GCP_version_for_variable_data_type. ",
                }
            )

    return invalid_records


"""Uniqueness within individual columns"""


def check_all_unique_values_cols(
    metadata_values: Dict[str, MetadataValues], template_map: Dict
) -> List[Dict]:

    cases = [
        (
            template_map["DatasetSeries_dataset_series_name"]["tab"],
            template_map["DatasetSeries_dataset_series_name"]["name"],
        ),
        (
            template_map[
                "DatasetSeries_google_cloud_platform_bigquery_table_name"
            ]["tab"],
            template_map[
                "DatasetSeries_google_cloud_platform_bigquery_table_name"
            ]["name"],
        ),
        (
            template_map["DatasetFile_file_path_and_name"]["tab"],
            template_map["DatasetFile_file_path_and_name"]["name"],
        ),
    ]

    mvs = []

    for case in cases:
        mvs.append(search_md_values(metadata_values, case[0], case[1]))

    invalid_records = []

    for mv in mvs:
        invalid_records.extend(_check_unique_values(mv))

    return invalid_records


def _check_unique_values(mv: MetadataValues) -> List[Dict]:
    duplicates = set([v for v in mv.values if mv.values.count(v) > 1])

    invalid_records = []

    for duplicate in duplicates:
        invalid_records.append(
            {
                "tab": mv.cell.tab,
                "name": mv.cell.name,
                "value": duplicate,
                "reason": "must_not_have_duplicate_values. ",
            }
        )
    return invalid_records


"""Uniqueness in one column within groups by another column"""


def check_Variables_duplicate_variable_names(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    return _check_duplicate_values(
        df,
        template_map["Variables_google_cloud_platform_bigquery_table_name"][
            "tab"
        ],
        template_map["Variables_google_cloud_platform_bigquery_table_name"][
            "name"
        ],
        template_map["Variables_variable_name"]["name"],
        "must_not_have_duplicate_variable_names_in_same_table. ",
    )


def check_CodesAndValues_duplicate_variable_names(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    return _check_duplicate_values(
        df,
        template_map[
            "CodesandValues_google_cloud_platform_bigquery_table_name"
        ]["tab"],
        template_map[
            "CodesandValues_google_cloud_platform_bigquery_table_name"
        ]["name"],
        template_map["CodesandValues_variable_name"]["name"],
        "must_not_have_duplicate_variable_names_in_same_table. ",
    )


def _check_duplicate_values(
    df: pd.DataFrame, tab: str, groupby_col: str, val_col: str, error_msg: str
) -> List[Dict]:
    invalid_variable_names = _get_duplicate_values(df, groupby_col, val_col)
    records = df.to_dict("records")

    invalid_records = []

    for record in records:
        for table, var_names in invalid_variable_names.items():
            if record[groupby_col] == table and record[val_col] in var_names:
                invalid_records.append(
                    {
                        "tab": tab,
                        "name": val_col,
                        "value": record[val_col],
                        "reason": error_msg,
                    }
                )
    return invalid_records


def _get_duplicate_values(
    df: pd.DataFrame, groupby_cols: Union[str, List[str]], val_col: str
) -> Dict:
    if isinstance(groupby_cols, str):
        groupby_cols = [groupby_cols]
    records = df.groupby(groupby_cols)[val_col].apply(list).to_dict()
    dupes = {}

    for table, variables in records.items():
        # count the lowered versions to catch issue #5
        lowered_variables = [v.lower() for v in variables]
        duplicated_vars = [
            v for v in variables if lowered_variables.count(v.lower()) > 1
        ]

        if duplicated_vars:
            dupes[table] = duplicated_vars

    return dupes


"""Columns that become mandatory based on value of other columns"""


def check_DatasetFile_multiple_files_to_append(
    df: pd.DataFrame,
    template_map: Dict,
) -> List[Dict]:

    table_col: str = template_map[
        "DatasetFile_google_cloud_platform_bigquery_table_name"
    ]["name"]
    file_col: str = template_map["DatasetFile_file_path_and_name"]["name"]
    append_col: str = template_map[
        "DatasetFile_is_this_file_one_of_a_sequence_to_be_appended_back_together_"
    ]["name"]

    records = df.to_dict("records")
    dupe_tables = _check_multiple_files_to_same_table(df, table_col, file_col)

    invalid_records = []

    for record in records:
        if record[table_col] in dupe_tables and record[append_col] != "Yes":
            invalid_records.append(
                {
                    "tab": "Dataset File",
                    "name": append_col,
                    "value": record[append_col],
                    "reason": "must_be_yes_if_multiple_files_for_same_table. ",
                }
            )
    return invalid_records


def _check_multiple_files_to_same_table(
    df: pd.DataFrame, table_col: str, file_col: str
) -> List:
    records = df.groupby([table_col])[file_col].unique().to_dict()
    return [table for table, files in records.items() if len(files) > 1]


def check_DatasetFile_csv_column_separators(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    tab = template_map["DatasetFile_file_format"]["tab"]
    format_name = template_map["DatasetFile_file_format"]["name"]
    col_sep_name = template_map["DatasetFile_column_seperator"]["name"]

    records = df.to_dict("records")
    invalid_records = []

    for record in records:
        if record[format_name].upper() == "CSV" and record[
            col_sep_name
        ] not in [
            ",",
            "|",
            "\\t",
        ]:
            invalid_records.append(
                {
                    "tab": tab,
                    "name": col_sep_name,
                    "value": record[col_sep_name],
                    "reason": "must_have_separator_if_csv. ",
                }
            )
    return invalid_records


def check_DatasetFile_csv_number_of_header_rows(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    tab = template_map["DatasetFile_file_format"]["tab"]
    format_name = template_map["DatasetFile_file_format"]["name"]
    header_rows_name = template_map["DatasetFile_number_of_header_rows"][
        "name"
    ]

    records = df.to_dict("records")
    invalid_records = []

    for record in records:
        if (
            record[format_name].upper() == "CSV"
            and int(record[header_rows_name]) <= 0
        ):
            invalid_records.append(
                {
                    "tab": tab,
                    "name": header_rows_name,
                    "value": record[header_rows_name],
                    "reason": "Invalid number of header rows. ",
                }
            )

    return invalid_records


def check_DatasetFile_csv_string_identifier(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    tab = template_map["DatasetFile_file_format"]["tab"]
    format_name = template_map["DatasetFile_file_format"]["name"]
    str_id_name = template_map["DatasetFile_string_identifier"]["name"]

    records = df.to_dict("records")
    invalid_records = []

    for record in records:
        if record[format_name].upper() == "CSV" and record[str_id_name] in [
            "",
            "None",
            None,
            np.nan,
            "nan",
        ]:
            invalid_records.append(
                {
                    "tab": tab,
                    "name": str_id_name,
                    "value": record[str_id_name],
                    "reason": "Invalid string identifier. ",
                }
            )

    return invalid_records


def check_Variables_foreign_key_file_name(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    tab = template_map["Variables_foreign_key_file_name"]["tab"]
    for_key_file_name = template_map["Variables_foreign_key_file_name"]["name"]
    for_key_var_name = template_map["Variables_foreign_key_variable_name"][
        "name"
    ]
    is_for_key_name = template_map["Variables_is_foreign_key"]["name"]

    records = df.to_dict("records")
    invalid_records = []

    for record in records:
        if record[is_for_key_name].upper() == "YES":
            if record[for_key_file_name] in [
                "",
                "None",
                None,
                np.nan,
                "nan",
            ]:
                invalid_records.append(
                    {
                        "tab": tab,
                        "name": for_key_file_name,
                        "value": record[for_key_file_name],
                        "reason": "Must populate foreign key file name. ",
                    }
                )
            if record[for_key_var_name] in [
                "",
                "None",
                None,
                np.nan,
                "nan",
            ]:

                invalid_records.append(
                    {
                        "tab": tab,
                        "name": for_key_var_name,
                        "value": record[for_key_var_name],
                        "reason": "Must populate foreign key variable name. ",
                    }
                )

    return invalid_records


def check_Variables_variable_length_precision(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    tab = template_map["Variables_variable_data_type"]["tab"]
    var_dtype = template_map["Variables_variable_data_type"]["name"]
    var_len_pres = template_map["Variables_variable_length_precision"]["name"]

    records = df.to_dict("records")
    invalid_records = []

    for record in records:
        if record[var_dtype] in ["string", "float"] and record[
            var_len_pres
        ] in [
            "",
            "None",
            None,
            np.nan,
            "nan",
        ]:
            invalid_records.append(
                {
                    "tab": tab,
                    "name": var_len_pres,
                    "value": record[var_len_pres],
                    "reason": "Invalid variable length/precision. ",
                }
            )

    return invalid_records


def check_Variables_null_values_denoted_by(
    df: pd.DataFrame, template_map: Dict
) -> List[Dict]:
    tab = template_map["Variables_variable_data_type"]["tab"]
    var_null = template_map["Variables_nullability"]["name"]
    var_null_type = template_map["Variables_null_values_denoted_by"]["name"]

    records = df.to_dict("records")
    invalid_records = []

    for record in records:
        if record[var_null].upper() == "NULL" and record[var_null_type] in [
            "",
            None,
            np.nan,
        ]:
            invalid_records.append(
                {
                    "tab": tab,
                    "name": var_null_type,
                    "value": record[var_null_type],
                    "reason": "Missing null value description. ",
                }
            )

    return invalid_records
