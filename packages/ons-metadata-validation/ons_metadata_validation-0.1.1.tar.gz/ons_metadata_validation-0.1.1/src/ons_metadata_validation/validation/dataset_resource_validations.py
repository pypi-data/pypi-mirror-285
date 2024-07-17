from typing import Sequence, Tuple

import ons_metadata_validation.validation._validation_checks as vc
from ons_metadata_validation.validation._validation_constants import (
    STRING_HYGIENE_CHECKS,
)
from ons_metadata_validation.validation._validation_utils import (
    check_fails,
)

######################
"""Dataset Resource"""
######################


def validate_DatasetResource_dataset_resource_name(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_with_spaces,
        vc.must_be_within_length_80,
    ] + STRING_HYGIENE_CHECKS

    soft_checks = [vc.must_have_no_obvious_acronyms]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_acronym(values: Sequence) -> Tuple:
    hard_checks = [] + STRING_HYGIENE_CHECKS
    soft_checks = [
        vc.must_have_no_full_stops_in_acronym,
        vc.must_not_include_spaces,
    ]  # we want one acronym only
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# no checks
def validate_DatasetResource_significant_changes(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_data_creator(values: Sequence) -> Tuple:
    hard_checks = [] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_have_no_obvious_acronyms, vc.must_not_say_ONS]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_data_contributors(values: Sequence) -> Tuple:
    return validate_DatasetResource_data_creator(values)


# no checks
def validate_DatasetResource_purpose_of_this_dataset_resource(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_search_keywords(values: Sequence) -> Tuple:
    hard_checks = [vc.must_not_include_pipes] + STRING_HYGIENE_CHECKS
    soft_checks = [
        vc.must_start_with_capital,
        vc.must_have_no_more_than_five_list_items,
        vc.must_have_caps_after_commas,
    ]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_DatasetResource_dataset_theme(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# could add check looking for the specific renderings of "england & wales"
# that we don't like
# otherwise just hygiene
def validate_DatasetResource_geographic_level(values: Sequence) -> Tuple:
    hard_checks = [] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# no checks
def validate_DatasetResource_provenance(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# + contingent check for later: must match number of rows on corresponding sheet
def validate_DatasetResource_number_of_dataset_series(
    values: Sequence,
) -> Tuple:
    hard_checks = [vc.must_be_1_or_greater]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_number_of_structural_data_files(
    values: Sequence,
) -> Tuple:
    hard_checks = [vc.must_be_1_or_greater]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_date_of_completion(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_in_short_date_format,
        vc.must_have_no_leading_apostrophe,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_have_short_date_in_plausible_range]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_name_and_email_of_individual_completing_this_template(
    values: Sequence,
) -> Tuple:
    hard_checks = [
        vc.must_contain_an_email_address,
        vc.must_have_comma_and_space,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_DatasetResource_security_classification(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_DatasetResource_dataset_resource_type(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_number_of_non_structural_reference_files(
    values: Sequence,
) -> Tuple:
    hard_checks = [vc.must_be_0_or_greater]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_DatasetResource_number_of_code_list_files(
    values: Sequence,
) -> Tuple:
    hard_checks = [vc.must_be_0_or_greater]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)
