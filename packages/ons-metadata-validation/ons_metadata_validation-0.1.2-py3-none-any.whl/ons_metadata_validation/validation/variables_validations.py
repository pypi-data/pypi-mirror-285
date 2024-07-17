from typing import Sequence, Tuple

import ons_metadata_validation.validation._validation_checks as vc
from ons_metadata_validation.validation._validation_constants import (
    STRING_HYGIENE_CHECKS,
)
from ons_metadata_validation.validation._validation_utils import (
    check_fails,
)
from ons_metadata_validation.validation.dataset_file_validations import (
    validate_DatasetFile_notes,
)
from ons_metadata_validation.validation.dataset_series_validations import (
    validate_DatasetSeries_google_cloud_platform_bigquery_table_name,
)


# TODO: each name here should appear in the appropriate column on other sheets,
# and vice versa
def validate_Variables_google_cloud_platform_bigquery_table_name(
    values: Sequence,
) -> Tuple:
    return validate_DatasetSeries_google_cloud_platform_bigquery_table_name(
        values
    )


def validate_Variables_variable_name(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_with_underscores,
        vc.must_be_all_lower_case,  # TODO: need to settle whether this is needed
        vc.must_be_within_length_300,
        vc.must_not_start_with_digit,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_Variables_google_cloud_platform_compatible_variable_name(
    values: Sequence,
) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_with_underscores,
        vc.must_be_all_lower_case,
        vc.must_be_within_length_300,
        vc.must_not_start_with_digit,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_Variables_variable_label(values: Sequence) -> Tuple:
    # Discussed with Ama. Length limit might be 1024...
    # ...but leave at 300 until we hear otherwise.
    hard_checks = [
        vc.must_be_alphanumeric_with_spaces,
        vc.must_be_within_length_300,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_Variables_variable_description(values: Sequence) -> Tuple:
    # note that the difference between this and the other "description" fields
    # is intentional. 1024 characters is a limit imposed by GCP.
    hard_checks = [
        vc.must_be_within_length_1024,
        vc.must_end_with_a_full_stop_or_question_mark,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO check for JSON format (mandatory if file format=JSON)
# TODO: if we want to, we could check that the numbers in the sequence form a contiguous
# run, with no duplicates (for each file)
def validate_Variables_position_in_file(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_1_or_greater,
    ]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# Just an enum (I think the current plan is to leave these functions in as dummies, tho)
def validate_Variables_personally_identifiable_information(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_Variables_variable_data_type(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_valid_datatype,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO check this is populated and corresponds to prev columns
def validate_Variables_gcp_data_type(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_valid_gcp_datatype,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO: this is another one that could be given as a string or an int, so we need to
# decide how to handle that - probably expect one, but force the dtype and see if it
# passes other checks if needed?
# Also
# a "/" has been stripped from the name here; we could put a _ in its place, but
# we'd need to check that it matches up elsewhere in the code.
def validate_Variables_variable_lengthprecision(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_have_intelligible_length_precision,
        vc.must_not_talk_in_terms_of_decimal_places,  # apparently common, hence specific check
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_Variables_variable_format(values: Sequence) -> Tuple:
    hard_checks = [] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_resemble_a_date_format_specification]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_Variables_is_primary_key(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_Variables_is_foreign_key(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO treat as mandatory if foreign key = Yes
# note that Ama says anything to do with this variable is currently out of scope
# for her anyway
def validate_Variables_foreign_key_file_name(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO treat as mandatory if foreign key = Yes
def validate_Variables_foreign_key_variable_name(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_Variables_nullability(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO treat as mandatory if nullability = Null
# interestingly, since one of the valid options is ' ', we shouldn't do the usual
# leading and trailing spaces check here.
def validate_Variables_null_values_denoted_by(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = [vc.must_have_plausible_null_identifier]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# free text; nothing we can do automatically for this one
def validate_Variables_variable_constraints(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# free text; nothing we can do automatically for this one
def validate_Variables_applicable_business_rules(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_Variables_is_this_a_code(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_Variables_notes(values: Sequence) -> Tuple:
    return validate_DatasetFile_notes(values)
