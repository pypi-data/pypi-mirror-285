import dataclasses

from psycopg2 import sql


@dataclasses.dataclass
class Params:
    schema: str = "schema"
    table: str = "table"
    columns: str = "columns"
    aggregate: str = "aggregate"
    conditions: str = "conditions"
    conjunction: str = "conjunction"
    order_by: str = "order_by"
    group_by: str = "group_by"
    limit: str = "limit"


@dataclasses.dataclass
class StandardKeywords:
    ALL_COLUMNS: str = "*"
    WHERE: str = "WHERE"
    AND: str = "AND"
    OR: str = "OR"
    GREATER: str = ">"
    LESSER: str = "<"
    EQUALS: str = "="
    NOT_EQUALS: str = "!="
    BETWEEN: str = "BETWEEN"
    GREATER_OR_EQUALS: str = ">="
    LESS_OR_EQUALS: str = "<="
    LIKE: str = "LIKE"
    NOT: str = "NOT"
    ASCENDING: str = "ASC"
    DESCENDING: str = "DESC"


@dataclasses.dataclass
class Query:
    schema: str | None
    table: str | None
    columns: str | None = StandardKeywords.ALL_COLUMNS  # by default returns all columns
    aggregate: str | None = None
    conditions: dict[str, dict[str, str]] | None = None
    conjunction: str | None = None
    order_by: str | dict[str, str] | None = None
    group_by: str | None = None
    limit: str | None = None

    def __post_init__(self):
        if self.aggregate:
            if not self.group_by:
                raise ValueError("'aggregate' is required when 'group_by' is set")

        if self.columns == StandardKeywords.ALL_COLUMNS:
            # self.columns = self._get_column_names(self.schema, self.table)
            raise NotImplementedError

    def build(self) -> sql.SQL:
        query = sql.SQL("SELECT ").format()

        if self.aggregate:
            columns_sql = [
                sql.SQL("{}({})").format(sql.SQL(self.aggregate.get(column)), sql.Identifier(
                        column)) if column in self.aggregate else sql.Identifier(column)
                for column in self.columns
            ]

        else:
            columns_sql = [sql.Identifier(column) for column in self.columns]

        # Constructing the complete SELECT statement
        query = sql.SQL("SELECT {}").format(sql.SQL(', ').join(columns_sql))

        query += sql.SQL(" FROM {}.{}").format(
                sql.Identifier(self.schema),
                sql.Identifier(self.table)
        )

        if self.conditions is not None:
            operators = {_operator for _column, (_operator, _value) in self.conditions.items()}
            where_clause = sql.SQL("WHERE ")
            spl_columns = ["BETWEEN"]

            if any(_o.upper() in operators for _o in spl_columns):
                # eg: {"time_stamp": ("BETWEEN", ["2024-01-26 00:00:00", "2024-01-27 00:00:00"]) }
                between_conditions = [sql.SQL("{column} {operator} {value1} AND {value2}").format(
                        column=sql.Identifier(_c),
                        operator=sql.SQL(_o.upper()),
                        value1=sql.Literal(_v[0]),
                        value2=sql.Literal(_v[1])
                ) for _c, (_o, _v) in self.conditions.items() if _o in spl_columns if _o == "BETWEEN"]

                where_clause = where_clause + sql.SQL(f' {self.conjunction} ').join(between_conditions)

                # remove special condition from the conditions dictionary
                conditions = {column: (value, operator) for column, (operator, value) in self.conditions.items() if
                              operator.upper() not in spl_columns}

            if len(self.conditions.keys()) > 0:
                if where_clause != sql.SQL("WHERE "):
                    where_clause = where_clause + sql.SQL(f' {self.conjunction} ')

                conditions = [(sql.Identifier(column), sql.Literal(value), sql.SQL(
                        operator)) for column, (operator, value) in self.conditions.items()]

                where_clause = where_clause + sql.SQL(f' {self.conjunction} ').join(
                        sql.SQL("{column} {operator} {value}").format(
                                column=column,
                                operator=operator,
                                value=value
                        )
                        for column, value, operator in conditions
                )

            query += sql.SQL(" {where_clause}").format(
                    where_clause=where_clause
            )

            if self.group_by is not None:
                query += sql.SQL(" GROUP BY {group}").format(
                        group=sql.SQL(', ').join(map(sql.Identifier, self.group_by))
                )

            if self.order_by is not None:
                if isinstance(self.order_by, str):
                    self.order_by = {self.order_by: "ASC"}

                order_by = [(sql.Identifier(column), sql.SQL(direction))
                            for column, direction in self.order_by.items()]

                order_by_clause = sql.SQL(', ').join(
                        sql.SQL("{column} {direction}").format(
                                column=column,
                                direction=direction
                        )
                        for column, direction in order_by
                )
                query += sql.SQL(" ORDER BY {order_by_clause}").format(
                        order_by_clause=order_by_clause
                )

            if self.limit is not None:
                query += sql.SQL(" LIMIT {limit}").format(limit=sql.Literal(self.limit))

            return query
