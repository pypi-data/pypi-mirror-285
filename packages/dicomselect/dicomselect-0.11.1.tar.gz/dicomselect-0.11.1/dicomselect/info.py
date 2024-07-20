from typing import TYPE_CHECKING, Dict, List

import pandas as pd

if TYPE_CHECKING:
    from dicomselect.query import Query


class Info:
    """
    This helper object provides information of the parent Query.
    """
    def __init__(self, *args):
        parent, rows, cols = args
        self._query_parent: Query = parent
        self._rows: list[tuple] = rows
        self._cols: dict[str, dict[str, int]] = cols

    @property
    def count(self) -> int:
        return len(self._rows)

    @property
    def query(self) -> 'Query':
        return self._query_parent

    def to_string(self, sort_by_homogeneous: bool = True) -> str:
        """
        The current results of a query as a str.

        Args:
            sort_by_homogeneous:
                Sort by homogeneous columns. (default = True)
        """
        sort_by_similarity = sorted(
            sorted(self._cols.keys()),
            key=lambda k: len(self._cols[k]),
            reverse=not sort_by_homogeneous
        )

        contents = [f'Total selected DICOMs: {self.count}']
        contents.append('=' * len(contents[0]))

        for key in sort_by_similarity:
            contents.append(key)
            items = sorted(self._cols[key].items(), key=lambda a: a[1], reverse=True)
            for value, count in items:
                count: str = f'({count})'.ljust(len(str(len(self._rows))) + 2)
                contents.append(f'\t{count} {value}')

        return '\n'.join(contents)

    def to_df(self) -> pd.DataFrame:
        """
        The current results of a query as a pandas DataFrame. This function is untested.
        """
        return pd.DataFrame(data=self._rows, columns=["idx"] + list(self._cols.keys()))

    def include(self, *columns) -> 'Info':
        """
        Recreate the Info object filtered down to the provided columns.

        Args:
            columns: Columns to filter down to.
        """
        included_cols = {key: value for key, value in self._cols.items() if key in columns}
        return Info(self._query_parent, self._rows, included_cols)

    def exclude(self, *columns, recommended: bool = True, exclude_all_distinct: bool = False, exclude_none_distinct: bool = False) -> 'Info':
        """
        Recreate the Info object, excluding the provided columns.

        Args:
            columns:
                Columns to filter down to.
            recommended:
                Exclude columns that the author considers not useful in most cases. (most UID values, physical positions)
            exclude_all_distinct:
                Exclude columns where every value is unique.
            exclude_none_distinct:
                Exclude columns where all values are the same.
        """
        r = [k for k in self._cols.keys() if 'uid' in k] + \
            ['dicomselect_uid', 'image_position_patient', 'patient_position']

        def included(key, value):
            key_not_in_columns = key not in columns
            key_not_in_r = key not in r if recommended else True
            not_all_distinct = len(value) < self.count if exclude_all_distinct else True
            not_none_distinct = len(value) > 1 if exclude_none_distinct else True
            return all([key_not_in_columns, key_not_in_r, not_all_distinct, not_none_distinct])

        included_cols = {key: value for key, value in self._cols.items() if included(key, value)}
        return Info(self._query_parent, self._rows, included_cols)

    def __str__(self) -> str:
        return self.to_string()
