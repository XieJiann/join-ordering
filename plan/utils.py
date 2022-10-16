from catalog.catalog import Table
from plan.expr import Expression, ExpressionType


def make_column_ref(table: Table, column_name: str) -> Expression:
    return Expression(ExpressionType.ColumnRef, (), table.get(column_name))


def make_true() -> Expression:
    return Expression(ExpressionType.ConstantVal, (), True)
