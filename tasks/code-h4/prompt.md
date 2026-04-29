You are given a Python SQL query builder that has a subtle bug when handling nested OR conditions combined with IN clauses containing NULL values.

```python
"""SQL query builder with support for complex WHERE clauses."""
from typing import Any, List, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field

class Op(Enum):
    EQ = "="
    NE = "!="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    LIKE = "LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"

@dataclass
class Condition:
    column: str
    op: Op
    value: Any = None

@dataclass
class ConditionGroup:
    conditions: List[Union['Condition', 'ConditionGroup']]
    logic: str = "AND"  # AND or OR

@dataclass
class OrderBy:
    column: str
    direction: str = "ASC"

@dataclass
class JoinClause:
    table: str
    on: str
    join_type: str = "INNER"

class QueryBuilder:
    def __init__(self, table: str):
        self.table = table
        self._select: List[str] = ["*"]
        self._where: Optional[ConditionGroup] = None
        self._order_by: List[OrderBy] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._joins: List[JoinClause] = []
        self._group_by: List[str] = []
        self._having: Optional[ConditionGroup] = None
        self._params: List[Any] = []

    def select(self, *columns: str) -> 'QueryBuilder':
        self._select = list(columns)
        return self

    def where(self, *conditions: Union[Condition, ConditionGroup]) -> 'QueryBuilder':
        if len(conditions) == 1 and isinstance(conditions[0], ConditionGroup):
            self._where = conditions[0]
        else:
            self._where = ConditionGroup(conditions=list(conditions), logic="AND")
        return self

    def order_by(self, column: str, direction: str = "ASC") -> 'QueryBuilder':
        self._order_by.append(OrderBy(column=column, direction=direction))
        return self

    def limit(self, n: int) -> 'QueryBuilder':
        self._limit = n
        return self

    def offset(self, n: int) -> 'QueryBuilder':
        self._offset = n
        return self

    def join(self, table: str, on: str, join_type: str = "INNER") -> 'QueryBuilder':
        self._joins.append(JoinClause(table=table, on=on, join_type=join_type))
        return self

    def group_by(self, *columns: str) -> 'QueryBuilder':
        self._group_by = list(columns)
        return self

    def having(self, *conditions: Union[Condition, ConditionGroup]) -> 'QueryBuilder':
        if len(conditions) == 1 and isinstance(conditions[0], ConditionGroup):
            self._having = conditions[0]
        else:
            self._having = ConditionGroup(conditions=list(conditions), logic="AND")
        return self

    def build(self) -> Tuple[str, List[Any]]:
        self._params = []
        parts = [f"SELECT {', '.join(self._select)}"]
        parts.append(f"FROM {self.table}")

        for j in self._joins:
            parts.append(f"{j.join_type} JOIN {j.table} ON {j.on}")

        if self._where:
            where_sql = self._build_condition_group(self._where)
            parts.append(f"WHERE {where_sql}")

        if self._group_by:
            parts.append(f"GROUP BY {', '.join(self._group_by)}")

        if self._having:
            having_sql = self._build_condition_group(self._having)
            parts.append(f"HAVING {having_sql}")

        if self._order_by:
            order_parts = [f"{o.column} {o.direction}" for o in self._order_by]
            parts.append(f"ORDER BY {', '.join(order_parts)}")

        if self._limit is not None:
            parts.append(f"LIMIT {self._limit}")

        if self._offset is not None:
            parts.append(f"OFFSET {self._offset}")

        return " ".join(parts), self._params

    def _build_condition_group(self, group: ConditionGroup) -> str:
        parts = []
        for cond in group.conditions:
            if isinstance(cond, ConditionGroup):
                sub = self._build_condition_group(cond)
                parts.append(f"({sub})")
            elif isinstance(cond, Condition):
                parts.append(self._build_condition(cond))
        return f" {group.logic} ".join(parts)

    def _build_condition(self, cond: Condition) -> str:
        if cond.op == Op.IS_NULL:
            return f"{cond.column} IS NULL"
        if cond.op == Op.IS_NOT_NULL:
            return f"{cond.column} IS NOT NULL"
        if cond.op == Op.BETWEEN:
            self._params.extend(cond.value)
            return f"{cond.column} BETWEEN ? AND ?"
        if cond.op in (Op.IN, Op.NOT_IN):
            values = cond.value if isinstance(cond.value, (list, tuple)) else [cond.value]
            # BUG: Does not handle NULL values in IN clause
            # SQL: col IN (1, 2, NULL) does NOT match rows where col IS NULL
            # Correct: (col IN (1, 2) OR col IS NULL)
            placeholders = ", ".join(["?" for _ in values])
            self._params.extend(values)
            op_str = "IN" if cond.op == Op.IN else "NOT IN"
            return f"{cond.column} {op_str} ({placeholders})"
        self._params.append(cond.value)
        return f"{cond.column} {cond.op.value} ?"


# Helper functions
def and_(*conditions) -> ConditionGroup:
    return ConditionGroup(conditions=list(conditions), logic="AND")

def or_(*conditions) -> ConditionGroup:
    return ConditionGroup(conditions=list(conditions), logic="OR")

def eq(col: str, val: Any) -> Condition:
    return Condition(column=col, op=Op.EQ, value=val)

def ne(col: str, val: Any) -> Condition:
    return Condition(column=col, op=Op.NE, value=val)

def lt(col: str, val: Any) -> Condition:
    return Condition(column=col, op=Op.LT, value=val)

def gt(col: str, val: Any) -> Condition:
    return Condition(column=col, op=Op.GT, value=val)

def in_(col: str, vals: List[Any]) -> Condition:
    return Condition(column=col, op=Op.IN, value=vals)

def not_in(col: str, vals: List[Any]) -> Condition:
    return Condition(column=col, op=Op.NOT_IN, value=vals)

def is_null(col: str) -> Condition:
    return Condition(column=col, op=Op.IS_NULL)

def between(col: str, low: Any, high: Any) -> Condition:
    return Condition(column=col, op=Op.BETWEEN, value=[low, high])
```

Your tasks:
1. **Find the bug**: Explain what happens when IN/NOT IN clauses contain NULL values, especially nested inside OR groups.
2. **Write a failing test** that demonstrates the bug with a concrete query.
3. **Fix the bug** so that:
   - `IN` with NULL values generates `(col IN (non-null-vals) OR col IS NULL)`
   - `NOT IN` with NULL values generates `(col NOT IN (non-null-vals) AND col IS NOT NULL)`
   - This works correctly when nested inside OR/AND groups (proper parenthesization).
4. Return the complete fixed code with your failing test included as a function.
