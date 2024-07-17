import re
from datetime import datetime
from typing import Union

from ons_metadata_validation.reference.lookups import GCP_TYPE_LOOKUP
from ons_metadata_validation.validation._validation_utils import (
    _regex_match,
    _regex_search,
)

##############
"""CONTENTS"""
##############

# functions related to...

# acceptable charactersets
# forbidden characters
# string hygiene
# grammar
# acronyms
# length
# integers
# dates
# substrings
# lookups


"""functions related to basic string hygiene"""


def must_not_start_with_whitespace(item: str) -> bool:
    """ "pass case" -> True

    "pass_case " -> True

    " fail case" -> False"""
    if not isinstance(item, str):
        raise TypeError(
            f"must_not_start_with_whitespace expected type str but got {type(item)}"
        )
    return item[0] != " "


def must_not_end_with_whitespace(item: str) -> bool:
    """ "pass case" -> True

    " pass_case" -> True

    "fail case " -> False"""
    if not isinstance(item, str):
        raise TypeError(
            f"must_not_end_with_whitespace expected type str but got {type(item)}"
        )
    return item[-1] != " "


def must_not_contain_double_spaces(item: str) -> bool:
    """ "pass case" -> True

    " pass_case" -> True

    "fail  case" -> False"""
    if not isinstance(item, str):
        raise TypeError(
            f"must_not_contain_double_spaces expected type str but got {type(item)}"
        )
    return not _regex_search(r"  ", item)


"""functions related to acceptable charactersets"""


def must_be_alphanumeric_only(item: str) -> bool:
    """ "test" -> True
    "test_fail3235" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"[^a-zA-Z0-9]", item)


def must_be_alphanumeric_with_spaces(item: str) -> bool:
    """ "pass case" -> True
    "passcase" -> True
    "fail_case" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"[^a-zA-Z0-9 ]", item)


def must_be_alphanumeric_with_underscores(item: str) -> bool:
    """ "test_case" -> True
    "test case" -> False
    "test_c@se" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"[^a-zA-Z0-9_]", item)


def must_be_alphanumeric_with_spaces_or_underscores(item: str) -> bool:
    """ "pass_case1" -> True
    "pass case2" -> True
    "fail case!" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"[^a-zA-Z0-9_ ]", item)


def must_be_alphanumeric_with_dashes(item: str) -> bool:
    """ "pass-case1" -> True

    "passcase-2" -> True

    "fail case" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"[^a-zA-Z0-9\-]", item)  # aka kebab-case


def must_be_all_lower_case(item: str) -> bool:
    """ "testcase" -> True

    "TestCase" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"[A-Z]", item)


"""functions related to forbidden characters"""


def must_not_start_with_digit(item: str) -> bool:
    """ "testcase1" -> True

    "1TestCase" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_match(r"^\d", item)


# considered making a "not this" function to riff on and decided against it for now
def must_not_include_spaces(item: str) -> bool:
    """ "passcase" -> True

    "pass_case" -> True

    "fail case" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r" ", item)


def must_not_include_pipes(item: str) -> bool:
    """ "pass case" -> True

    "pass_case" -> True

    "fail|case" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"\|", item)


def must_not_include_backslashes(item: str) -> bool:
    """ "pass case" -> True

    "pass_case" -> True

    "fail\\case" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"\\", item)


"""functions related to grammar"""


def must_start_with_capital(item: str) -> bool:
    """ "Passcase" -> True

    "failcase" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return item[0].isupper()


def must_have_comma_and_space(item: str) -> bool:
    """ "pass, case" -> True

    "fail case," -> False

    "fail" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return _regex_search(r", ", item)


def must_have_caps_after_commas(item: str) -> bool:
    """ "pass, Case" -> True

    "fail, case" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r",\s?[a-z]", item)


def must_end_with_a_full_stop_or_question_mark(item: str) -> bool:
    """
    "pass case." -> True

    "fail case!" -> False

    "fail" -> False"""
    if not isinstance(item, str):
        raise TypeError(
            f"must_end_with_a_full_stop_or_question_mark() expected type str but got {type(item)}"
        )
    # note that, per discussion, ! is not acceptable for tone reasons
    return item[-1] in [".", "?"]


"""functions related to acronyms"""


def must_have_no_full_stops_in_acronym(item: str) -> bool:
    """ "PASS" -> True

    "F.A.I.L." -> False

    "FAI.L" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"\b(?:[A-Z]\.?)*\.[A-Z](?:\.?[A-Z])*\b", item)


def must_have_no_obvious_acronyms(item: str) -> bool:
    """ "pass case" -> True

    "F.A.I.L." -> False

    "FAIL" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")

    # can expand whitelist later if needed
    whitelist = ["UK"]
    chunks = item.split(" ")
    allcaps = [chunk for chunk in chunks if chunk.isupper() and len(chunk) > 1]
    badcaps = [
        capword
        for capword in allcaps
        if re.sub(r"[^A-Z]", "", capword) not in whitelist
    ]
    return not bool(badcaps)


def must_not_say_ONS(item: str) -> bool:
    """ "ONS" -> False

    "O.N.S." -> False

    "O N S" -> False

    "pass" -> True"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"O\s*\.?\s*N\s*\.?\s*S", item)


"""functions related to length"""


def must_be_within_length_limit(item: str, max_len: int) -> bool:
    """Checks if string length is less than the maximum length specified"""
    if not all([isinstance(item, str), isinstance(max_len, int)]):
        raise TypeError(
            "must_be_within_length_limit expects arg types: [str, int], "
            f"received: [{type(item).__name__}, {type(max_len).__name__}]"
        )
    return bool(len(item) < max_len)


def must_be_within_length_50(item: str) -> bool:
    """Checks if string is less than 50 characters long"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return must_be_within_length_limit(item, 50)


def must_be_within_length_80(item: str) -> bool:
    """Checks if string is less than 80 characters long"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return must_be_within_length_limit(item, 80)


def must_be_within_length_160(item: str) -> bool:
    """Checks if string is less than 100 characters long"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return must_be_within_length_limit(item, 160)


def must_be_within_length_300(item: str) -> bool:
    """Checks if string is less than 300 characters long"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return must_be_within_length_limit(item, 300)


def must_be_within_length_1024(item: str) -> bool:
    """Checks if string is less than 1024 characters long"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return must_be_within_length_limit(item, 1024)


def must_be_within_length_1800(item: str) -> bool:
    """Checks if string is less than 1800 characters long"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return must_be_within_length_limit(item, 1800)


def must_be_exactly_32_chars(item: str) -> bool:
    """Checks if string is exactly 32 characters long"""
    if not isinstance(item, str):
        raise TypeError(
            f"must_be_exactly_32_chars() expected type str but got {type(item)}"
        )
    return len(item) == 32


# could parameterize later if needed
def must_have_no_more_than_five_list_items(item: str) -> bool:
    """ "a, b, c, d" -> True

    "a, b, c, d, e, f" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    comma_count = re.findall(",", item)
    return len(comma_count) < 5


"""functions related to integers"""


def must_be_integer(item: int) -> bool:
    """1, True
    "1", False"""
    return isinstance(item, int)


def must_be_above_min_value(
    item: Union[int, float], min: Union[int, float]
) -> bool:
    """Example if mimimum value is 0:
    1 -> True
    -1 -> False"""
    if not all(
        [isinstance(item, (float, int)), isinstance(min, (float, int))]
    ):
        raise TypeError(
            "must_be_above_min_value expects arg types: [(float, int), (float, int)], "
            f"received: [{type(item).__name__}, {type(min).__name__}]"
        )
    return item >= min


def must_be_0_or_greater(item: Union[int, float]) -> bool:
    """0 -> True

    -1 -> False"""
    return must_be_above_min_value(item, 0)


def must_be_1_or_greater(item: Union[int, float]) -> bool:
    """1 -> True

    0 -> False"""
    return must_be_above_min_value(item, 1)


"""functions related to dates"""


def _trial_by_datetime(item: str, format: str) -> Union[datetime, bool]:
    """Checks if date and date format is accepted by datetime, for example:
    date: "15/05/2024",   date format: "%d/%m/%Y" -> True
    date: "5 April 2024", date format: "%d %B %Y" -> True
    date: "15/05/2024",   date format: "%W %X %Y" -> False"""
    if not all([isinstance(item, str), isinstance(format, str)]):
        raise TypeError(
            "_trial_by_datetime expects arg types: [str, str], "
            f"received: [{type(item).__name__}, {type(format).__name__}]"
        )
    try:
        date = datetime.strptime(item, format)  # e.g. 10/05/2024
        return date
    except ValueError:  # if datetime doesn't like the format
        return False


def _date_in_plausible_range(item: str, format: str) -> bool:
    """Checks if date and date format is accepted by datetime and if date plausible:
    date: "15/05/2024",   date format: "%d/%m/%Y" -> True
    date: "15/05/1824",   date format: "%d/%m/%Y" -> False
    date: "15/05/2025",   date format: "%d/%m/%Y" -> False
    date: "15/05/2024",   date format: "%W %X %Y" -> False"""
    date = _trial_by_datetime(item, format)
    if not isinstance(date, datetime):
        return False
    if date > datetime.today() or date < datetime(year=1900, month=1, day=1):
        return False
    return True


def must_be_in_short_date_format(item: str) -> bool:
    """ "5/4/2024" -> True

    "15 May 2024" -> False"""
    date = _trial_by_datetime(item, "%d/%m/%Y")  # e.g. 10/05/2024
    return bool(date)


def must_have_short_date_in_plausible_range(item: str) -> bool:
    """ "15/05/2024" -> True

    "15/05/1824" -> False

    "15/05/2025" -> False"""
    return _date_in_plausible_range(item, "%d/%m/%Y")


def must_be_in_long_date_format(item: str) -> bool:
    """ "15 May 2024" -> True

    "15/05/2024" -> False

    "fail case" -> False"""
    if not all([isinstance(item, str)]):
        raise TypeError(
            "must_be_in_long_date_format expects arg types: [str], "
            f"received: [{type(item).__name__}]"
        )
    dates_out = []
    for in_date in item.split(" to "):
        dates_out.append(
            _trial_by_datetime(in_date, "%d %B %Y")
        )  # e.g. 10 May 2024

    return all(dates_out)  # True iff all dates successfully evaluate


def must_have_long_date_in_plausible_range(item: str) -> bool:
    """ "15 May 2024" -> True

    "15 May 1824" -> False

    "15 May 2025" -> False"""
    if not all([isinstance(item, str)]):
        raise TypeError(
            "must_have_long_date_in_plausible_range expects arg types: [str], "
            f"received: [{type(item).__name__}]"
        )
    end_date = item.split(" to ")[-1]
    return _date_in_plausible_range(end_date, "%d %B %Y")  # e.g. 10 May 2024


def must_have_no_leading_apostrophe(item: str) -> bool:
    """ "pass" -> True

    "'fail" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")

    return _regex_search(r"^[^'`]", item)


# can genericise later if we ever need to look at long format dates for this check
def must_be_date_in_future(item: str) -> bool:
    """ "15/05/2024" -> False

    "15/05/1824" -> False

    "15/05/3025" -> True"""
    date = _trial_by_datetime(item, "%d/%m/%Y")  # e.g. 10/05/2024
    if not isinstance(date, datetime):
        return False
    return date > datetime.today()


def must_be_date_in_past(item: str) -> bool:
    """ "15/05/2024" -> True

    "15/05/1824" -> True

    "15/05/3025" -> False"""
    date = _trial_by_datetime(item, "%d/%m/%Y")  # e.g. 10/05/2024
    if not isinstance(date, datetime):
        return False
    return date < datetime.today()


def must_resemble_a_date_format_specification(item: str) -> bool:
    """'dd-MMM-yyyy' -> True
    'DD-mm-YYYY' -> False
    'Day/Month/Year' -> False
    """
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search(r"[^yMdHms. \-\/]", item)


"""functions seeking specific substrings"""


def must_contain_an_email_address(item: str) -> bool:
    """ "pass_case@test.co.uk" -> True

    "failcase1test.co.uk" -> False

    "failcase2@test" -> False

    "sdfawefjwoj.comskfjawe@" -> False"""
    # exhaustive regex for all and only valid emails would be extremely lengthy
    # here we just want a rough check for whethe they've provided something
    # that plausibly looks like it could be an email address
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return _regex_search(
        r"[a-zA-Z0-9.]{3,}@[a-zA-Z0-9.]{3,}.(com|uk|org)", item
    )


def must_be_valid_url(item: str) -> bool:
    """ "www.pass.com" -> True

    "https://www.pass.com" -> True

    "https:/www.fail.com" -> False"""
    """
    Notes
    short, permissive url regex courtesy of gskinner at https://regexr.com/3e6m0
    """
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return _regex_match(
        r"^(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=]*)$",
        item,
    )


def must_not_be_ons_sharepoint_url(item: str) -> bool:
    """ "www.passcase.com" -> True

    "www.officenationalstatistics.sharepoint.com" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return not _regex_search("officenationalstatistics.sharepoint.com", item)


def must_have_plausible_filepath(item: str) -> bool:
    """ "long/pass/case.parquet" -> True

    "pass/case.parquet/subfile.json" -> True

    "pass/case.csv/subfile.csv" -> True

    "this/should.csv/fail" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")

    # at least one slash, ends with <.extension>
    return _regex_match(
        r"^[A-Za-z0-9_&%\(\)\/.]+\/[A-Za-z0-9_&%\(\)\/.]+.(?i:csv|json|jsonl|parquet)$",
        item,
    )


def must_have_timestamp_in_filename(item: str) -> bool:
    """ "fail_case.parquet" -> False

    "pass_case_20240604_120000.parquet" -> True"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")

    timestamp = re.findall(r"(?<!\d)\d{8}_\d{6}(?!\d)", item)
    if timestamp:
        date = _trial_by_datetime(timestamp[0], "%Y%m%d_%H%M%S")
        return bool(date)
    return False


def must_have_intelligible_file_size_unit(item: str) -> bool:
    """ "B" -> True

    "KB" -> True

    "MB" -> True

    "GB" -> True

    "fail" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    # would we accept this in words ("kilobytes" etc? Surely nobody would do this?)
    acceptable_units = ["B", "KB", "MB", "GB"]
    return item.upper() in acceptable_units


# TODO: will we accept anything other than UTF-8?
def must_be_valid_encoding(item: str) -> bool:
    """ "UTF-8" -> True

    "fail" -> False"""
    if not all([isinstance(item, str)]):
        raise TypeError(
            f"must_be_valid_encoding() expected types: [str] "
            f"received: [{type(item).__name__}]"
        )
    encodings_list = ["UTF-8"]

    return bool(any(enc in item for enc in encodings_list))


def must_not_talk_in_terms_of_decimal_places(item: str) -> bool:
    """ "3 dp" -> False

    "2 d.p." -> False

    "3 decimal places" -> False

    "3" -> True"""
    if not all([isinstance(item, str)]):
        raise TypeError(
            f"expected types: [str] " f"received: [{type(item).__name__}]"
        )
    dps = ["dp", "d.p.", "decimal places"]
    return all([dp not in item.lower() for dp in dps])


def must_have_intelligible_length_precision(item: str) -> bool:
    """ "3" -> True

    "3, 4" -> True

    "2.0" -> False

    "fail" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")

    if "." in item:  # don't want it expressed as a decimal
        return False

    elif item.count(",") > 1:
        return False

    elif item.count(",") == 0:
        try:
            item = int(item)  # should just be intelligible as a number...
            return True
        except ValueError:
            return False

    elif item.count(",") == 1:
        lhs, rhs = item.split(",")  # ...or else look like "#,#"
        try:
            lhs = int(lhs)
            rhs = int(rhs)
            return True
        except ValueError:
            return False


def must_have_plausible_null_identifier(item: str) -> bool:
    """ " " -> True

    "#N/A" -> True

    "N/A" -> True

    "n/a" -> True"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")

    # the most likely suspects from the default list used by pandas for
    # spotting null indicators
    plausible_nulls = [
        " ",
        "#N/A",
        "N/A",
        "n/a",
        "#NA",
        "NA",
        "NaN",
        "nan",
        "Null",
        "null",
        "None",
        "none",
    ]

    return item in plausible_nulls


def is_poc_pipe_prod(item: str) -> bool:
    """ "ons-ids-poc-pipe-prod" -> True

    "ons-ids-poc-pipe-prod " -> False

    "fail" -> False"""
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return item == "ons-ids-poc-pipe-prod"


def must_be_zero_dot_followed_by_four_digits(item: float) -> bool:
    """0.1234 -> True
    1.23 -> False
    """
    str_item = str(item)
    return _regex_match(r"^0.\d\d\d\d$", str_item)


"""Functions that refer to lookups"""


def must_be_valid_datatype(item: str) -> bool:
    """ "INT32" -> True

    "INT64" -> False

    "FLOAT" -> True

    "FLOAT64" -> False"""
    if not isinstance(item, str):
        raise TypeError(
            f"must_be_valid_datatype() expected type str but got {type(item)}"
        )
    return item.upper() in GCP_TYPE_LOOKUP.keys()


def must_be_valid_gcp_datatype(item: str) -> bool:
    """ "INT32" -> False

    "INT64" -> True

    "FLOAT" -> False

    "FLOAT64" -> True"""
    if not isinstance(item, str):
        raise TypeError(
            f"must_be_valid_datatype() expected type str but got {type(item)}"
        )
    return item.upper() in GCP_TYPE_LOOKUP.values()


"""original functions from Ed"""

# def has_duplicates(item: List[str]) -> bool:
#     if not isinstance(item, list):
#         raise TypeError(
#             f"has_duplicates() expected type list but got {type(item)}"
#         )
#     return len(item) != len(set(item))
