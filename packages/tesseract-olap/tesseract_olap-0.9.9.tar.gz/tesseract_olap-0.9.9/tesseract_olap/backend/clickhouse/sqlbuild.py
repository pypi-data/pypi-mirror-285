"""ClickHouse SQL generation module.

Comprises all the functions which generate SQL code, through the pypika library.
"""

import logging
from itertools import chain
from typing import Callable, Optional, Set, Tuple, Union

import immutables as immu
from pyparsing import ParseResults
from pypika import analytics as an
from pypika import functions as fn
from pypika.dialects import ClickHouseQuery, QueryBuilder
from pypika.enums import Arithmetic, Order
from pypika.queries import AliasedQuery, Selectable, Table
from pypika.terms import (
    ArithmeticExpression,
    Case,
    Criterion,
    Field,
    Function,
    LiteralValue,
    PyformatParameter,
    Term,
    ValueWrapper,
)

from tesseract_olap.backend import ParamManager
from tesseract_olap.query import (
    Comparison,
    DataQuery,
    LogicOperator,
    MeasureField,
    MembersQuery,
    NumericConstraint,
    RestrictionAge,
)
from tesseract_olap.schema import MemberType, models

from .dialect import ArrayElement, AverageWeighted, Median, Power, Quantile, TopK

logger = logging.getLogger("tesseract_olap.backend.clickhouse")


def dataquery_sql(query: DataQuery) -> Tuple[Selectable, ParamManager]:
    """Build the query which will retrieve an aggregated dataset from the
    database.

    The construction of this query has two main parts:
    - The Core Query,
        which retrieves all the columns needed for later steps, and applies the
        filter on the qualitative fields (cuts)
    - The Grouping Query,
        which applies the calculations/aggregations over the data, filters on
        quantitative fields (filters), applies pagination, sorting and the
        aliases over the columns

    The returned query is composed by the Grouping query on the Core query as
    subquery.
    """
    meta = ParamManager()

    def _convert_table(
        table: Union[models.Table, models.InlineTable], alias: Optional[str]
    ):
        if isinstance(table, models.Table):
            return Table(table.name, schema=table.schema, alias=alias)
        else:
            meta.set_table(table)
            return Table(table.name, alias=alias)

    def _get_table(
        table: Union[models.Table, models.InlineTable, None],
        *,
        alias: Optional[str] = None,
    ) -> Table:
        return table_fact if table is None else _convert_table(table, alias)

    locale = query.locale
    table_fact = _convert_table(query.cube.table, "tfact")
    tfact_is_subset = query.cube.subset_table

    def dataquery_tcore_sql() -> Selectable:
        """
        Build the query which will create the `core_table`, an intermediate query
        which contains all data from the Dimension Tables and the Fact Table the
        cube is associated to.

        This query also retrieves the row for all associated dimensions used in
        drilldowns and cuts, through a LEFT JOIN using the foreign key.
        """
        qb: QueryBuilder = ClickHouseQuery.from_(table_fact)

        qb = qb.select(
            *(
                # from the fact table, get the fields which contain the values
                # to aggregate and filter; ensure to not duplicate key_columns
                Field(
                    item.measure.key_column,
                    alias=f"ms_{item.alias_key}",
                    table=table_fact,
                )
                for item in dict(
                    (obj.alias_key, obj) for obj in query.fields_quantitative
                ).values()
                if isinstance(item.measure, models.Measure)
            )
        )

        for hiefi in query.fields_qualitative:
            table_dim = _get_table(hiefi.table, alias=f"ft_{hiefi.alias}")

            field_fkey = table_fact.field(hiefi.foreign_key)

            columns: Set[Field] = set()

            for lvlfi in hiefi.levels:
                # apply cuts to fact table to reduce amount of data to aggregate later
                caster = lvlfi.level.type_caster
                members_include = sorted(caster(mem) for mem in lvlfi.members_include)
                members_exclude = sorted(caster(mem) for mem in lvlfi.members_exclude)

                lvl_columns = [
                    Field(column, table=table_dim, alias=f"lv_{alias}")
                    for column, _, alias in lvlfi.iter_columns(locale)
                ]

                if table_dim is table_fact:
                    if len(members_include) > 0:
                        qb = qb.where(
                            table_fact.field(lvlfi.key_column).isin(members_include)
                        )

                    if len(members_exclude) > 0:
                        qb = qb.where(
                            table_fact.field(lvlfi.key_column).notin(members_exclude)
                        )

                elif lvlfi.key_column == hiefi.primary_key:
                    # for _yield_lvlfi_columns, index 0 is the ID column
                    lvl_columns[0] = Field(
                        hiefi.foreign_key, table=table_fact, alias=lvl_columns[0].alias
                    )

                    if len(members_include) > 0:
                        qb = qb.where(field_fkey.isin(members_include))

                    if len(members_exclude) > 0:
                        qb = qb.where(field_fkey.notin(members_exclude))

                elif lvlfi.is_cut:
                    subq = ClickHouseQuery.from_(table_dim).select(hiefi.primary_key)

                    if len(members_include) > 0:
                        subq = subq.where(
                            table_dim.field(lvlfi.key_column).isin(members_include)
                        )

                    if len(members_exclude) > 0:
                        subq = subq.where(
                            table_dim.field(lvlfi.key_column).notin(members_exclude)
                        )

                    qb = qb.where(field_fkey.isin(subq))

                if lvlfi.is_drilldown:
                    columns.update(lvl_columns)

                # apply arbitrary time restrictions
                # can't be handled as a cut because depends on a value we don't know
                if lvlfi.time_restriction is not None:
                    # this is equivalent to having a cut set on this level,
                    # for the members that match the time scale
                    order = (
                        Order.asc
                        if lvlfi.time_restriction.age == RestrictionAge.OLDEST
                        else Order.desc
                    )

                    # we intend to create a subquery on the fact table for all
                    # possible members of the relevant level/timescale, using
                    # distinct unify, and get the first in the defined order
                    # which translates into latest/oldest

                    # TODO: use EXPLAIN to see if DISTINCT improves or worsens the query
                    qb_time: QueryBuilder = (
                        ClickHouseQuery.from_(table_fact).distinct().limit(1)
                    )
                    field_time = table_dim.field(lvlfi.key_column)

                    if table_dim is table_fact:
                        # Hierarchy is defined in the fact table -> direct query
                        qb = qb.where(
                            field_time
                            == qb_time.select(
                                table_fact.field(lvlfi.key_column)
                            ).orderby(table_fact.field(lvlfi.key_column), order=order)
                        )

                    elif lvlfi.key_column == hiefi.primary_key:
                        # The level column is used as foreign key for the fact table
                        qb = qb.where(
                            field_fkey
                            == qb_time.select(
                                table_fact.field(hiefi.primary_key)
                            ).orderby(table_fact.field(hiefi.primary_key), order=order)
                        )

                    else:
                        qb = qb.where(
                            field_time
                            == qb_time.left_join(table_dim)
                            .on(field_fkey == table_dim.field(hiefi.primary_key))
                            .select(table_dim.field(lvlfi.key_column))
                            .orderby(table_dim.field(lvlfi.key_column), order=order)
                        )

            qb = qb.select(*sorted(columns, key=lambda x: x.name))

            # we must do LEFT JOIN if the request needs a column from a table
            # other than fact table; this includes PK columns for cuts on members
            # not in the fact table
            if table_dim is not table_fact and (
                any(field.table is not table_fact for field in columns)
                or any(
                    item
                    for item in hiefi.levels
                    if item.is_cut or item.time_restriction
                )
            ):
                qb = qb.left_join(table_dim).on(
                    table_dim.field(hiefi.primary_key) == field_fkey
                )

            # if the hierarchy is not stored on the fact table and the fact table
            # combines facts for multiple levels, apply a filter over the
            # foreign keys matching the members of the requested level
            if table_dim is not table_fact and tfact_is_subset:
                qb = qb.where(
                    field_fkey.isin(
                        ClickHouseQuery.from_(table_dim)
                        .select(hiefi.primary_key)
                        .distinct()
                    )
                )

        return qb.as_("tcore")

    def dataquery_tgroup_sql(tcore: Selectable) -> Selectable:
        """
        Builds the query which will perform the grouping by drilldown members, and
        then the aggregation over the resulting groups.
        """
        qb: QueryBuilder = ClickHouseQuery.from_(tcore)

        level_columns = immu.Map(
            (column_name, f"lv_{column_alias}")
            for hiefi in query.fields_qualitative
            for lvlfi in hiefi.levels
            for _, column_name, column_alias in lvlfi.iter_columns(query.locale)
        )

        def _yield_measures(msrfi: MeasureField):
            if isinstance(msrfi.measure, models.Measure):
                yield _get_aggregate(tcore, msrfi)

            if isinstance(msrfi.measure, models.CalculatedMeasure):
                formula = msrfi.measure.formula
                yield _transf_formula(formula, _translate_col).as_(msrfi.name)

            # Creates Ranking columns using window functions
            if msrfi.with_ranking is not None:
                yield an.Rank(alias=f"{msrfi.name} Ranking").orderby(
                    Field(msrfi.name),
                    order=Order.asc if msrfi.with_ranking == "asc" else Order.desc,
                )

        def _translate_col(column: str):
            return Field(
                level_columns.get(column, column),
                table=tcore if column in level_columns else None,
            )

        measure_fields = (
            term
            for msrfi in query.fields_quantitative
            for term in _yield_measures(msrfi)
        )

        level_fields = (
            Field(f"lv_{alias}", alias=name, table=tcore)
            for hiefi in query.fields_qualitative
            for lvlfi in hiefi.drilldown_levels
            for _, name, alias in lvlfi.iter_columns(locale)
        )

        qb = qb.select(*measure_fields, *level_fields)

        # Use the representative levels, so the data gets aggregated
        groupby_fields = (
            tcore.field(f"lv_{alias}")
            for hiefi in query.fields_qualitative
            for lvlfi in hiefi.drilldown_levels
            for _, _, alias in lvlfi.iter_columns(locale)
        )
        qb = qb.groupby(*groupby_fields)

        # Default sorting directions
        # The results are sorted by the ID column of each drilldown
        order = Order.asc
        orderby = (
            tcore.field(f"lv_{hiefi.deepest_level.alias}")
            for hiefi in query.fields_qualitative
            if hiefi.has_drilldowns
        )
        # Flag to know an user-defined sorting field hasn't been set
        sort_field = None

        # Apply user-defined filters on aggregated data
        for msrfi in query.fields_quantitative:
            # skip field if no filter is defined
            if not msrfi.constraint:
                continue

            # create criterion for first constraint
            column = Field(msrfi.name)
            criterion = _get_filter_criterion(column, msrfi.constraint[0])
            # add second constraint to criterion if defined
            if len(msrfi.constraint) == 3:
                criterion2 = _get_filter_criterion(column, msrfi.constraint[2])
                if msrfi.constraint[1] == LogicOperator.AND:
                    criterion &= criterion2
                elif msrfi.constraint[1] == LogicOperator.OR:
                    criterion |= criterion2
            qb = qb.having(criterion)

        for hiefi in query.fields_qualitative:
            # skip field if is not a drilldown
            if not hiefi.has_drilldowns:
                continue

            # User-defined sorting directions for Properties
            if sort_field is None and query.sorting:
                sort_field, sort_order = query.sorting
                # TODO: this method could still use a drilldown for sorting, check
                field_finder = (
                    tcore.field(f"lv_{alias}")
                    for lvlfi in hiefi.drilldown_levels
                    for _, name, alias in lvlfi.iter_columns(locale)
                    if name == sort_field
                )
                sort_field = next(field_finder, None)
                if sort_field is not None:
                    order = Order.asc if sort_order == "asc" else Order.desc
                    orderby = chain((sort_field,), orderby)

        # User-defined sorting directions for Measures
        if sort_field is None and query.sorting:
            sort_field, sort_order = query.sorting
            field_finder = (
                Field(msrfi.name)
                for msrfi in query.fields_quantitative
                if msrfi.name == sort_field
            )
            sort_field = next(field_finder, None)
            if sort_field is not None:
                order = Order.asc if sort_order == "asc" else Order.desc
                orderby = chain((sort_field,), orderby)

        qb = qb.orderby(*orderby, order=order)

        # apply pagination parameters if values are higher than zero
        pag_limit, pag_offset = query.pagination
        if pag_limit > 0:
            qb = qb.limit(pag_limit)
        if pag_offset > 0:
            qb = qb.offset(pag_offset)

        return qb.as_("tgroup")

    table_core = dataquery_tcore_sql()
    table_group = dataquery_tgroup_sql(table_core)

    if len([1 for msrfi in query.fields_quantitative if not msrfi.is_measure]) > 0:
        drilldowns = (
            column_name
            for hiefi in query.fields_qualitative
            for lvlfi in hiefi.drilldown_levels
            for _, column_name, _ in lvlfi.iter_columns(locale)
        )
        measures = (
            measure.name
            for msrfi in query.fields_quantitative
            if msrfi.is_measure
            for measure in msrfi.measure.and_submeasures()
        )
        table_with = (
            ClickHouseQuery.with_(table_group, "mq")
            .from_(AliasedQuery("mq"))
            .select(*drilldowns, *measures)
        )
        return table_with, meta

    return table_group, meta


def membersquery_sql(query: MembersQuery) -> Tuple[Selectable, ParamManager]:
    """Build the query which will list all the members of a Level in a dimension
    table.

    Depending on the filtering parameters set by the user, this list can also
    be limited by pagination, search terms, or members observed in a fact table.
    """
    meta = ParamManager()

    def _convert_table(
        table: Union[models.Table, models.InlineTable], alias: Optional[str]
    ):
        if isinstance(table, models.Table):
            return Table(table.name, schema=table.schema, alias=alias)
        else:
            meta.set_table(table)
            return Table(table.name, alias=alias)

    locale = query.locale
    hiefi = query.hiefield

    table_fact = _convert_table(query.cube.table, "tfact")

    table_dim = (
        table_fact if hiefi.table is None else _convert_table(hiefi.table, "tdim")
    )

    ancestor_columns = tuple(
        (alias, column_name)
        for depth, lvlfi in enumerate(hiefi.levels[:-1])
        for alias, column_name in (
            (f"ancestor.{depth}.key", lvlfi.level.key_column),
            (f"ancestor.{depth}.caption", lvlfi.level.get_name_column(locale)),
        )
        if column_name is not None
    )
    level_columns = ancestor_columns + tuple(
        (alias, column_name)
        for alias, column_name in (
            ("key", hiefi.deepest_level.level.key_column),
            ("caption", hiefi.deepest_level.level.get_name_column(locale)),
        )
        if column_name is not None
    )

    # if the level's primary key doesn't match its hierarchy's primary key
    # the lookup must be done against a subquery
    if hiefi.deepest_level.key_column != hiefi.primary_key:
        fields_left = (column_name for _, column_name in level_columns)
        table_left = ClickHouseQuery.from_(table_dim).select(*fields_left).distinct()
    else:
        table_left = table_dim

    level_fields = tuple(
        Field(column_name, alias=alias, table=table_left)
        for alias, column_name in level_columns
    )

    qb: QueryBuilder = (
        ClickHouseQuery.from_(table_dim)
        .select(*level_fields)
        .distinct()
        .orderby(*level_fields, order=Order.asc)
    )

    pagination = query.pagination
    if pagination.limit > 0:
        qb = qb.limit(pagination.limit)
    if pagination.offset > 0:
        qb = qb.offset(pagination.offset)

    if query.search is not None:
        pname = meta.set_param(f"%{query.search}%")
        param = PyformatParameter(pname)
        search_criterion = Criterion.any(
            Field(field).ilike(param)  # type: ignore
            for lvlfield in query.hiefield.levels
            for field in (
                lvlfield.level.key_column
                if lvlfield.level.key_type == MemberType.STRING
                else None,
                lvlfield.level.get_name_column(locale),
            )
            if field is not None
        )
        qb = qb.where(search_criterion)

    return qb, meta


def _get_aggregate(
    table: Selectable, msrfi: MeasureField
) -> Union[Function, ArithmeticExpression]:
    """Generates an AggregateFunction instance from a measure, including all its
    parameters, to be used in the SQL query.
    """
    field = table.field(f"ms_{msrfi.alias_key}")
    # alias = f"ag_{msrfi.alias_name}"
    alias = msrfi.name

    if msrfi.aggregator_type == "Sum":
        return fn.Sum(field, alias=alias)

    elif msrfi.aggregator_type == "Count":
        return fn.Count(field, alias=alias)

    elif msrfi.aggregator_type == "Average":
        return fn.Avg(field, alias=alias)

    elif msrfi.aggregator_type == "Max":
        return fn.Max(field, alias=alias)

    elif msrfi.aggregator_type == "Min":
        return fn.Min(field, alias=alias)

    elif msrfi.aggregator_type == "Mode":
        return ArrayElement(TopK(1, field), 1, alias=alias)

    # elif msrfi.aggregator_type == "BasicGroupedMedian":
    #     return fn.Abs()

    # elif msrfi.aggregator_type == "WeightedSum":
    #     return fn.Abs()

    elif msrfi.aggregator_type == "WeightedAverage":
        params = msrfi.aggregator_params
        weight_field = ValueWrapper(params["weight_column"])
        return AverageWeighted(field, weight_field, alias=alias)

    # elif msrfi.aggregator_type == "ReplicateWeightMoe":
    #     return fn.Abs()

    elif msrfi.aggregator_type == "CalculatedMoe":
        params = msrfi.aggregator_params
        critical_value = ValueWrapper(params["critical_value"])
        term = fn.Sqrt(fn.Sum(Power(field / critical_value, 2)))
        return ArithmeticExpression(Arithmetic.mul, term, critical_value, alias=alias)

    elif msrfi.aggregator_type == "Median":
        return Median(field, alias=alias)

    elif msrfi.aggregator_type == "Quantile":
        params = msrfi.aggregator_params
        quantile_level = float(params["quantile_level"])
        return Quantile(quantile_level, field, alias=alias)

    # elif msrfi.aggregator_type == "WeightedAverageMoe":
    #     return fn.Abs()

    raise NameError(
        f"Clickhouse module not prepared to handle aggregation type: "
        f"{msrfi.aggregator_type}"
    )


def _get_filter_criterion(field: Field, constr: NumericConstraint):
    comparison, scalar = constr

    if comparison == Comparison.GT:
        return field.gt(scalar)
    elif comparison == Comparison.GTE:
        return field.gte(scalar)
    elif comparison == Comparison.LT:
        return field.lt(scalar)
    elif comparison == Comparison.LTE:
        return field.lte(scalar)
    elif comparison == Comparison.EQ:
        return field.eq(scalar)
    elif comparison == Comparison.NEQ:
        return field.ne(scalar)

    raise NameError(f"Invalid criterion type: {comparison}")


def _transf_formula(tokens, field_builder: Callable) -> Term:
    if isinstance(tokens, ParseResults):
        if len(tokens) == 1:
            return _transf_formula(tokens[0], field_builder)

        if tokens[0] == "CASE":
            case = Case()

            for item in tokens[1:]:
                if item[0] == "WHEN":
                    clauses = _transf_formula(item[1], field_builder)
                    expr = _transf_formula(item[3], field_builder)
                    case = case.when(clauses, expr)
                elif item[0] == "ELSE":
                    expr = _transf_formula(item[1], field_builder)
                    case = case.else_(expr)
                    break

            return case

        operator = tokens[1]
        assert isinstance(operator, str)

        if operator in ">= <= == != <>":
            branch_left = _transf_formula(tokens[0], field_builder)
            branch_right = _transf_formula(tokens[2], field_builder)

            if operator == ">":
                return branch_left > branch_right
            elif operator == "<":
                return branch_left < branch_right
            elif operator == ">=":
                return branch_left >= branch_right
            elif operator == "<=":
                return branch_left <= branch_right
            elif operator == "==":
                return branch_left == branch_right
            elif operator in ("!=", "<>"):
                return branch_left != branch_right

            raise ValueError(f"Operator '{operator}' is not supported")

        if operator in "+-*/%":
            branch_left = _transf_formula(tokens[0], field_builder)
            branch_right = _transf_formula(tokens[2], field_builder)

            if operator == "+":
                return branch_left + branch_right
            elif operator == "-":
                return branch_left - branch_right
            elif operator == "*":
                return branch_left * branch_right
            elif operator == "/":
                return branch_left / branch_right
            elif operator == "%":
                return branch_left % branch_right

            raise ValueError(f"Operator '{operator}' is not supported")

    elif isinstance(tokens, (int, float)):
        return ValueWrapper(tokens)

    elif isinstance(tokens, str):
        if tokens.startswith("'") and tokens.endswith("'"):
            return LiteralValue(tokens[1:-1])
        elif tokens.startswith('"') and tokens.endswith('"'):
            return LiteralValue(tokens[1:-1])
        else:
            return field_builder(tokens)

    logger.debug("Formula couldn't be parsed: %s, %r", type(tokens), tokens)
    raise ValueError(f"Expression '{tokens!r}' can't be parsed")
