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
from ons_metadata_validation.validation.dataset_series_validations import (
    validate_DatasetSeries_description,
    validate_DatasetSeries_frequency,
    validate_DatasetSeries_reference_period,
)


def validate_BackOffice_ids_business_catalogue_identifier(
    values: Sequence,
) -> Tuple:
    # this format should change eventually, but there's no set timeline
    hard_checks = [vc.must_be_zero_dot_followed_by_four_digits]
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_description(values: Sequence) -> Tuple:
    return validate_DatasetSeries_description(values)


def validate_BackOffice_abstract(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_within_length_160,
        vc.must_end_with_a_full_stop_or_question_mark,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# TODO kebab-case validation check
def validate_BackOffice_google_cloud_platform_project_name(
    values: Sequence,
) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_with_dashes,
        vc.must_be_all_lower_case,
        vc.must_be_within_length_1024,
        vc.must_not_start_with_digit,
    ] + STRING_HYGIENE_CHECKS

    soft_checks = [vc.is_poc_pipe_prod]
    # currently, you need a good reason not to be,
    # but we may remove this one at a later date
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_google_cloud_platform_big_query_dataset_name(
    values: Sequence,
) -> Tuple:
    hard_checks = [
        vc.must_be_alphanumeric_with_underscores,
        vc.must_be_all_lower_case,
        vc.must_be_within_length_1024,
        vc.must_not_start_with_digit,
    ] + STRING_HYGIENE_CHECKS

    soft_checks = [vc.must_be_within_length_50]
    # yes that's two length checks - one's an absolute limit, the other is recommended
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# no checks
def validate_BackOffice_other_unique_identifiers_for_dataset_resource(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# ah, this is the one that currently has a trailing underscore on the form itself
# enum only
def validate_BackOffice_frequency_(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return validate_DatasetSeries_frequency(values)


def validate_BackOffice_geographic_coverage(values: Sequence) -> Tuple:
    return validate_DatasetResource_geographic_level(values)


# TODO: we could check that the start is the earliest previously specified start,
# and that the end is the latest previously specified end
# and if it's missing, this could be a candidate for auto-inference
def validate_BackOffice_temporal_coverage(values: Sequence) -> Tuple:
    return validate_DatasetSeries_reference_period(
        values
    )  # these have different names, but they're the same thing


# enum only
def validate_BackOffice_sensitivity_status_for_dataset_resource(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_sensitivity_tool_url(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_valid_url,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_retention_date(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_in_short_date_format,
        vc.must_have_no_leading_apostrophe,
        vc.must_be_date_in_future,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# no checks
def validate_BackOffice_provider_statement_for_retention_removal_or_deletion(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_removal_date(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_in_short_date_format,
        vc.must_have_no_leading_apostrophe,
        vc.must_be_date_in_past,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_removal_comments(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_data_controller(values: Sequence) -> Tuple:
    hard_checks = [] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_have_no_obvious_acronyms]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_data_processor(values: Sequence) -> Tuple:
    hard_checks = [] + STRING_HYGIENE_CHECKS
    soft_checks = [vc.must_have_no_obvious_acronyms]
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_dataset_domain(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_legal_gateway(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# free text, no checks (except possibly hygiene if we want to)
def validate_BackOffice_other_legal_gateway(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_licensing_status(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_metadata_access(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


def validate_BackOffice_documentation(values: Sequence) -> Tuple:
    hard_checks = [
        vc.must_be_valid_url,
        vc.must_not_be_ons_sharepoint_url,
    ] + STRING_HYGIENE_CHECKS
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# no checks
def validate_BackOffice_what_are_the_linkage_requirements_for_the_data_within_the_project_scope(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# no checks
def validate_BackOffice_how_has_deidentification_been_achieved(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_should_this_dataset_be_visible_for_internal_or_external_users(
    values: Sequence,
) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_restrictions_for_access(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_research_outputs(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_project_approval(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_disclosure_control(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)


# enum only
def validate_BackOffice_research_disclaimer(values: Sequence) -> Tuple:
    hard_checks = []
    soft_checks = []
    return check_fails(values, hard_checks), check_fails(values, soft_checks)
