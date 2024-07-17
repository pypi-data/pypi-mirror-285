import re
from typing import Callable, Dict, List, Sequence


def _regex_search(pattern: str, item: str) -> bool:
    if not isinstance(item, str):
        raise TypeError(
            f"_regex_search() expected type str but got {type(item)}"
        )
    return bool(re.search(pattern, item))


def _regex_match(pattern: str, item: str) -> bool:
    if not isinstance(item, str):
        raise TypeError(
            f"_regex_match() expected type str but got {type(item)}"
        )
    return bool(re.match(pattern, item))


def check_fails(values: Sequence, checks: List[Callable]) -> Dict[str, str]:
    check_failures = {}

    # we now convert to set earlier so can just iterate over
    # values here
    for val in values:
        fails = ""
        for check_pass in checks:
            if not check_pass(val):
                fails += check_pass.__name__ + ". "
        if fails:
            if val not in check_failures:
                check_failures[val] = fails
            else:
                check_failures[val] += fails
    return check_failures
