from typing import TYPE_CHECKING, Dict, List, Tuple, Union

import pandas as pd

if TYPE_CHECKING:
    from dicomselect.queryfactory import QueryFactory

from dicomselect.info import Info


class Query:
    """
    Combine queries (a selection of rows from the database) with :func:`Database.plan` to plan out a conversion of your
    selection.

    Examples:
        >>> db = Database(db_path)
        >>> with db as query:
        >>>     query_0000 = query.where('patient_id', '=', 'ProstateX-0000').where('image_direction', '=', 'transverse')
        >>> db.plan(template_str, query_0000)
    """
    def __init__(self, *args):
        factory, name = args
        self._factory: QueryFactory = factory
        self._name: str = name or 'data'
        ids = factory.temp_tables[self._name]
        self._ids = ids[0]
        self._count = ids[1]
        self._info: Info | None = None

    @property
    def is_base(self) -> bool:
        """
        Whether this query is the base query obtained from the parent Database.
        """
        return not bool(self._name)

    @property
    def count(self) -> int:
        return self._count

    @property
    def columns(self):
        """
        Return a tuple containing the names of all the columns in the database.

        Returns:
            A tuple of column names.
        """
        return self._factory.columns

    @property
    def info(self):
        """
        Returns an Info object which can print out the current query selection.

        Info inherits the following functions: :func:`count`, :func:`to_string`, :func:`to_df`, :func:`include`
        and :func:`exclude`.
        """
        if not self._info:
            rows: List[tuple] = self._factory.execute(
                f'SELECT DISTINCT * FROM data WHERE id IN (SELECT id FROM {self._name})').fetchall()
            cols: Dict[Dict[str, int]] = dict()
            for i, c in enumerate(self.columns, 1):
                cols[c] = {}
                for r in rows:
                    value = r[i]
                    cols[c][value] = cols[c].get(value, 0) + 1
            self._info = Info(self, rows, cols)
        return self._info

    def to_string(self, sort_by_homogeneous: bool = True) -> str:
        """
        The current results of a query as a str.

        Args:
            sort_by_homogeneous:
                Sort by homogeneous columns. (default = True)
        """
        return self.info.to_string(sort_by_homogeneous)

    def to_df(self) -> pd.DataFrame:
        """
        The current results of a query as a pandas DataFrame. This function is untested.
        """
        return self.info.to_df()

    def include(self, *columns) -> Info:
        """
        Create an Info object, which filters down to the provided columns for printouts.

        Args:
            columns: Columns to filter down to.
        """
        return self.info.include(*columns)

    def exclude(self, *columns, recommended: bool = True, exclude_all_distinct: bool = False,
                exclude_none_distinct: bool = False) -> 'Info':
        """
        Create an Info object, which excludes the provided columns for printouts.

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
        return self.info.exclude(*columns, recommended=recommended, exclude_all_distinct=exclude_all_distinct,
                                 exclude_none_distinct=exclude_none_distinct)

    def distinct_values(self, column: str) -> List[str]:
        """
        Retrieve distinct values from a specified column.

        Args:
            column:
                The name of the column to retrieve distinct values from.
        """
        if not self.is_base:
            distinct: List[Tuple[str]] = self._factory.execute(
                f'SELECT DISTINCT {column} FROM data WHERE id IN (SELECT id FROM {self._name})'
            ).fetchall()
        else:
            distinct: List[Tuple[str]] = self._factory.execute(f'SELECT DISTINCT ({column}) FROM data').fetchall()
        return [d[0] for d in distinct]

    def where_raw(self, sql: str) -> 'Query':
        """
        Create a query based on a raw SQL query. Not recommended.

        Args:
            sql:
                SQL query. "... WHERE" is prefixed.

        Raises:
            ValueError:
                Invalid SQL.
        """
        return self._factory.create_query_from_sql('WHERE ' + sql, self._name if not self.is_base else '')

    def where(self, column: str, operator: str, values: Union[List[str], str], invert: bool = False) -> 'Query':
        """
        Filter the dataset based on the given column, operator, and values. The result can be combined with other queries
        using the union(), difference(), and intersect() methods.

        Args:
            column:
                Name of the column to query. The name is case-sensitive. The columns property can be used to obtain a list
                of all available columns.
            operator:
                Valid operators include '=', '<>', '!=', '>', '>=', '<', '<=', 'like', 'between', and 'in'.
            values:
                Values to query. Providing more values than expected will create OR chains, eg. (column='a') OR (column='b'),
                where appropriate.
            invert:
                Invert the query, by prefixing the query with a NOT.
        """
        loc = locals()
        self._factory.check_if_exists('column', self.columns, loc['column'])

        values = values if isinstance(values, list) else [values]
        values = [f"'{v}'" for v in values]
        len_values = len(values)
        valid_operators = '=', '<>', '!=', '>', '>=', '<', '<=', 'LIKE', 'BETWEEN', 'IN'
        operator = operator.upper()
        invert = 'NOT' if invert else ''
        assert len_values > 0, ValueError('expected values, got 0')

        if operator not in valid_operators:
            raise ValueError(f'{operator} is an invalid operator, valid operators are {valid_operators}')

        if operator == 'BETWEEN':
            if len(values) % 2 != 0:
                raise ValueError(f'expected an even number of values, got {len(values)}: {values}')
            values = [f'({column} BETWEEN {values[i]} AND {values[i + 1]})' for i in range(0, len(values), 2)]
        elif operator == 'IN':
            values = [f'{column} IN (' + ', '.join(values) + ')']
        else:
            values = [f'({column} {operator} {v})' for v in values]

        values = ' OR '.join(values)
        sql = f'WHERE {invert} ({values})'
        return self._factory.create_query_from_sql(sql, self._name if not self.is_base else '')

    def intersect(self, where: 'Query') -> 'Query':
        """
        Create a new view by intersecting the results of the specified queries.

        Args:
            where:
                The query to intersect. Leave empty to intersect using the last two queries.

        Raises
            ValueError
                If any of the specified queries do not exist.
        """
        return self._factory.create_query_from_set_operation(self._name, where._name, 'INTERSECT')

    def union(self, where: 'Query') -> 'Query':
        """
        Create a new query by taking the union of the results of the specified queries.

        Args:
            where:
                The query to union. Leave empty to union using the last two queries.

        Raises:
            ValueError
                If any of the specified queries do not exist.
        """
        return self._factory.create_query_from_set_operation(self._name, where._name, 'UNION')

    def difference(self, where: 'Query') -> 'Query':
        """
        Create a new query by taking the difference of the results of the specified queries.

        Args:
            where:
                The query to subtract.

        Raises:
            ValueError
                If any of the specified queries do not exist.
        """
        return self._factory.create_query_from_set_operation(self._name, where._name, 'EXCEPT')

    def __str__(self) -> str:
        return str(self.info.exclude())
