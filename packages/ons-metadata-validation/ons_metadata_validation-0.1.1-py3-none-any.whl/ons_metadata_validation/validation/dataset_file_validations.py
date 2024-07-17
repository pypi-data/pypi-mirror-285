from typing import Sequence, Tuple

import ons_metadata_validation.validation._validation_checks as vc
from ons_metadata_validation.validation._validation_constants import (
    STRING_HYGIENE_CHECKS,
)
from ons_metadata_validation.validation._validation_utils import (
    check_fails,
)
from ons_metadata_validation.validation.dataset_series_validations import (
    validate_DatasetSeries_description,
    validate_DatasetSeries_google_cloud_platform_bigquery_table_name,
    validate_DatasetSeries_reference_period,
)


# TODO: each name here should appear in the appropriate column on other sheets,
# and vice versa
def validate_DatasetFile_google_cloud_platform_bigquery_table_name(
    values: Sequence,
) -> Tuple:
    return validate_DatasetSeries_google_cloud_platform_bigquery_table_name(
        values
    )


def validate_DatasetFile_file_path_and_name(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_have_plausible_filepath,
        vc.must_not_include_backslashes,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_have_timestamp_in_filename]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# mandatory, enum, no other checks
def validate_DatasetFile_file_format(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO: mandatory if file format = CSV, should be blank if not
# mandatory, enum, no other checks
def validate_DatasetFile_column_seperator(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO: mandatory if file format = CSV, should be blank if not
# not sure if there's a reasonable list of possible valid string identifiers?
def validate_DatasetFile_string_identifier(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetFile_file_description(values: Sequence) -> Tuple:
    return validate_DatasetSeries_description(values)


# TODO: if we really want to, we could check that these dates are weakly within
# the corresponding period on dataset_series tab
def validate_DatasetFile_reference_period(values: Sequence) -> Tuple:
    return validate_DatasetSeries_reference_period(values)


# TODO check if int/float and use HDFS size to get the size to populate if not there
#
# don't think there's anything we can usefully check, since the plausible range
# depends on the unit - FG
def validate_DatasetFile_file_size(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO Should add an enum or separate check?
def validate_DatasetFile_file_size_unit(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_have_intelligible_file_size_unit
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# mandatory, enum, no other checks
def validate_DatasetFile_is_code_list(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO: I've asked Ama if this needs to be 1+ or if 0 is acceptable
def validate_DatasetFile_number_of_records(values: Sequence) -> Tuple:
    hard_checks = [vc.must_be_1_or_greater]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# mandatory, enum, no other checks
def validate_DatasetFile_is_this_file_one_of_a_sequence_to_be_appended_back_together(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetFile_number_of_header_rows(values: Sequence) -> Tuple:
    hard_checks = [vc.must_be_0_or_greater]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetFile_number_of_footer_rows(values: Sequence) -> Tuple:
    hard_checks = [vc.must_be_0_or_greater]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetFile_character_encoding(values: Sequence) -> Tuple:
    hard_checks = [vc.must_be_valid_encoding] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetFile_hash_value_for_checksum(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_only,
        vc.must_be_exactly_32_chars,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO: could enforce starting with a capital and ending with a full stop,
# but I don't think that's especially important / helpful on the scale of things
# also need to decide if this needs string hygiene
def validate_DatasetFile_notes(values: Sequence) -> Tuple:
    hard_checks = [vc.must_be_within_length_1800]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)
