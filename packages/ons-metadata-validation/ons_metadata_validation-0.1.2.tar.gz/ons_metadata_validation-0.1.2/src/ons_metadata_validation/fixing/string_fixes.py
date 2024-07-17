import re


def remove_whitespace(item: str) -> str:
    """strips leading/trailing whitespace from string

    Args:
        item (str): item with whitespace

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified str without leading/trailing whitespace
    """
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return item.strip()


def add_full_stop(item: str) -> str:
    """adds full stop to item. Strips the string first to avoid the following
    example where there is another whitespace character at the end of the string

    without stripping first:
    >>> "does not end with full stop. "
    >>> add_full_stop("does not end with full stop. ")
    >>> # output: "does not end with full stop. ."

    with stripping first:
    >>> "does not end with full stop. "
    >>> add_full_stop("does not end with full stop. ")
    >>> # output: "does not end with full stop."

    Args:
        item (str): item without a full stop at the end

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified item with full stop at the end
    """
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")

    item = item.strip()

    if item[-1] in ["?", ".", "!"]:
        return item
    return item + "."


def remove_multiple_spaces(item: str) -> str:
    """remove double, triple, n+ spaces and replace with single space

    Args:
        item (str): item with double+ spaces

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified item with only single spaces
    """
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return re.sub(r" +", r" ", item)


def replace_non_breaking_space(item: str):
    """replaces the non ascii character '\\xa0' with a single space.
    May add more chars as more are found.

    Args:
        item (str): item with '\\xa0'

    Raises:
        TypeError: expects str type only

    Returns:
        str: modified item with only single spaces
    """
    if not isinstance(item, str):
        raise TypeError(f"expected type str but got {type(item)}")
    return item.replace("\xa0", " ").strip()
