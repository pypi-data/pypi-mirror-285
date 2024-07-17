from typing import Sequence, Tuple

import ons_metadata_validation.validation._validation_checks as vc
from ons_metadata_validation.validation._validation_constants import (
    STRING_HYGIENE_CHECKS,
)
from ons_metadata_validation.validation._validation_utils import (
    check_fails,
)
from ons_metadata_validation.validation.dataset_resource_validations import (
    validate_DatasetResource_geographic_level,
)

######################
"""Dataset Series"""
######################


def validate_DatasetSeries_dataset_series_name(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_with_spaces,
        vc.must_not_start_with_digit,
        vc.must_be_within_length_1024,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO: each name here should appear in the appropriate column on other sheets,
# and vice versa
# TODO: table names must be unique within the list (here only)
def validate_DatasetSeries_google_cloud_platform_bigquery_table_name(
    values: Sequence,
) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_with_underscores,
        vc.must_be_all_lower_case,
        vc.must_not_start_with_digit,
        vc.must_be_within_length_1024,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetSeries_description(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_within_length_1800,
        vc.must_end_with_a_full_stop_or_question_mark,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = [
        vc.must_have_no_obvious_acronyms
    ]  # explicit req on back office, implicit here and dataset file?
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO: also needs to be within the overall reference period on back office tab
def validate_DatasetSeries_reference_period(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_in_long_date_format,
        vc.must_have_no_leading_apostrophe,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_have_long_date_in_plausible_range]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# mandatory, enum, no other checks
def validate_DatasetSeries_geographic_coverage(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return validate_DatasetResource_geographic_level(values)


# mandatory, enum, no other checks
def validate_DatasetSeries_frequency(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# mandatory, enum, no other checks
def validate_DatasetSeries_supply_type(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# no checks
def validate_DatasetSeries_wave_numbertime_period_covered_survey_only(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetSeries_links_to_online_documentation_and_other_useful_materials(
    values: Sequence,
) -> Tuple:
    hard_checks = [] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_be_valid_url]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)
