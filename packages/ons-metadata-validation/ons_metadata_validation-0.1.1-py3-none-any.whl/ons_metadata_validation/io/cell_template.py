import logging
from typing import (
    Callable,
    Collection,
    Dict,
    List,
    Set,
    Tuple,
)

import attr
import numpy as np
from attr.validators import gt, instance_of, is_callable, optional

from ons_metadata_validation.utils.logger import (
    compress_logging_value,
)

logger = logging.getLogger()


@attr.define
class MetadataCell:
    tab: str = attr.ib(validator=[instance_of(str)])
    name: str = attr.ib(validator=[instance_of(str)])
    ref_cell: str = attr.ib(validator=[instance_of(str)])
    value_col: str = attr.ib(validator=[instance_of(str)])
    column: bool = attr.ib(validator=[instance_of(bool)])
    row_start: int = attr.ib(validator=[instance_of(int), gt(0)])
    mandatory: bool = attr.ib(validator=[instance_of(bool)])
    enum: list = attr.ib(validator=[instance_of(list)])
    datatype: Callable = attr.ib(validator=[is_callable()])
    func: Callable = attr.ib(validator=[optional(is_callable())])


@attr.define
class MetadataValues:
    cell: MetadataCell = attr.ib(validator=[instance_of(MetadataCell)])
    values: list = attr.ib(validator=[instance_of(list)])
    hard_fails: dict = attr.ib(
        default=None, validator=[optional(instance_of(dict))], init=False
    )
    soft_fails: dict = attr.ib(
        default=None, validator=[optional(instance_of(dict))], init=False
    )

    def skip(self):
        self.hard_fails, self.soft_fails = {}, {}

    def validate(self) -> None:
        """validates all values in object.
        1. converts None and np.nan to strings
        2. checks for missing values
        3. converts all datatypes to cell.datatype
        4. checks enum if required
        5. check against the cell.func

        stores results in dicts
        """
        for key, val in locals().items():
            logger.debug(f"{key} = {compress_logging_value(val)}")

        # have to initialise to have something to unpack at the end
        # using a list to append the dicts as they were created took more
        # lines of comments to explain than this
        none_fails, enum_fails, hard_fails = {}, {}, {}

        # initialising to empty dicts in case not mandatory
        self.hard_fails, self.soft_fails = {}, {}

        # convert all nones to str representation this is important for the
        # fail dicts
        none_set = [None, np.nan]
        self._convert_set_to_string(none_set)

        unchecked_values = set(self.values)

        # remove nones and empty strings
        none_fails = self._values_in_collection_check(
            unchecked_values,
            ["None", "nan", ""],
            "missing_value. ",
            in_set_fail=True,
        )
        unchecked_values = self._remove_checked_values(
            unchecked_values, none_fails
        )

        # convert to required type before validating ignoring the string nones
        unchecked_values, uncastable_values = self._convert_to_cell_datatype(
            unchecked_values, {str(item) for item in none_set}
        )

        if self.cell.enum:
            enum_fails: Dict = self._values_in_collection_check(
                unchecked_values,
                self.cell.enum,
                "not_in_dropdown. ",
                in_set_fail=False,
            )
            unchecked_values = self._remove_checked_values(
                unchecked_values, enum_fails
            )

        # sort to avoid set being a different order each time
        hard_fails, self.soft_fails = self.cell.func(sorted(unchecked_values))

        self.hard_fails = {
            **uncastable_values,
            **none_fails,
            **enum_fails,
            **hard_fails,
        }

    def _values_in_collection_check(
        self,
        unchecked_values: Collection,
        value_set: Collection,
        error_message: str,
        in_set_fail: bool,
    ) -> Dict:
        """check if values are in collection or if they're not in the collection

        used in validate for the none_fails and enum_fails

        Args:
            unchecked_values (Collection): the unchecked values
            value_set (Collection): the values to check the unchecked values against
            error_message (str): the error to record if fails
            in_set_fail (bool): flag, fail if in value_set or if NOT in value_set

        Returns:
            Dict: a fail dict with the reasons
        """
        for key, val in locals().items():
            logger.debug(f"{key} = {compress_logging_value(val)}")
        value_fails = {}
        for val in set(unchecked_values):
            if in_set_fail:
                if val in value_set:
                    value_fails[val] = error_message
            else:
                if str(val) not in value_set:
                    value_fails[val] = error_message
        return value_fails

    def _remove_checked_values(
        self, unchecked_values: Collection, checked_dict: Dict
    ) -> Set:
        """remove values from unchecked_values if present in checked_dict.
        Filters the number of values that fail at each stage.

        Args:
            unchecked_values (Collection): the unchecked values
            checked_dict (Dict): a fail dict

        Returns:
            Set: the remaining unchecked values
        """
        for key, val in locals().items():
            logger.debug(f"{key} = {compress_logging_value(val)}")
        return set(unchecked_values).difference(set(checked_dict.keys()))

    def _convert_set_to_string(self, value_set: Collection) -> None:
        """convert values in self.values to string if in value_set

        Args:
            value_set (Collection): the values for items to turn into string
                generally None or np.nan
        """
        self.values = [
            str(val) if val in value_set else val for val in self.values
        ]

    def _convert_to_cell_datatype(
        self, unchecked_values: Set, none_set: Set
    ) -> Tuple[List, Dict]:
        """convert all values in unchecked_values to the required cell.datatype
        if item is not able to be safely casted, then record that failure in
        uncastable_values dict

        Args:
            unchecked_values (Set): the unchecked values
            none_set (Set): don't try to convert None or np.nan to datatype,
                this is caught earlier

        Returns:
            Tuple[List, Dict]: the unchecked values and the uncastable values
        """
        for key, val in locals().items():
            logger.debug(f"{key} = {compress_logging_value(val)}")
        tmp_values = []
        uncastable_values = {}

        for item in unchecked_values:
            if item in none_set:
                continue
            try:
                item = self.cell.datatype(item)
                tmp_values.append(item)
            except ValueError as e:
                logger.error(f"{item}: {e}")
                uncastable_values[item] = (
                    f"must be castable to {self.cell.datatype.__name__}"
                )

        unchecked_values = set(tmp_values)

        return sorted(unchecked_values), dict(
            sorted(uncastable_values.items())
        )
