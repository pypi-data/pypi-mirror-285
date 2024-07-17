import ons_metadata_validation.validation._validation_checks as vc

STRING_HYGIENE_CHECKS = [
    vc.must_not_start_with_whitespace,
    vc.must_not_end_with_whitespace,
    vc.must_not_contain_double_spaces,
]
