from contextlib import nullcontext as does_not_raise
import pytest

from app.querybuilder import QueryBuilder
import os

SQL_PATH = os.path.join(os.path.dirname(__file__), "SQL")


def test_file_not_found():
    QB = QueryBuilder(SQL_PATH)
    with pytest.raises(FileNotFoundError):
        QB.add_sql("bogus_file.sql")


def test_file_not_sql():
    QB = QueryBuilder(SQL_PATH)
    with pytest.raises(ValueError):
        QB.add_sql("not_sql")


def test_add_sql():
    QB = QueryBuilder(SQL_PATH)
    QB.add_sql("select_all_ships_limit_10.sql", new_line=False)
    assert QB.get_query_str() == "SELECT * FROM dim_ship LIMIT 10;"


def test_add_string():
    QB = QueryBuilder(SQL_PATH)
    QB.add_string("SELECT * FROM dim_ship LIMIT 10;", new_line=False)
    assert QB.get_query_str() == "SELECT * FROM dim_ship LIMIT 10;"


def test_add_where():
    QB = QueryBuilder(SQL_PATH)
    QB.add_string("SELECT * FROM dim_ship LIMIT 10", new_line=False)
    QB.add_where("ds.ship_id", ">", 2)
    QB.add_where("ds.ship_id", "<", 5)
    QB.end_query()
    assert QB.get_query_str() == "SELECT * FROM dim_ship LIMIT 10\nWHERE ds.ship_id > 2\nAND ds.ship_id < 5;"


def test_add_where_list_to_tuple():
    QB = QueryBuilder(SQL_PATH)
    params = {}
    QB.add_string("SELECT * FROM dim_ship LIMIT 10", new_line=False)
    QB.add_where("ds.ship_id", "IN", [2], params)
    QB.end_query()
    assert QB.get_query_str() == "SELECT * FROM dim_ship LIMIT 10\nWHERE ds.ship_id IN :param0;"


def test_format_query():
    qb = QueryBuilder(SQL_PATH)
    placeholders = {"RELATION": "dim_ship"}
    qb.add_string("SELECT * FROM {RELATION} LIMIT 10", new_line=False).format_query(placeholders)
    assert qb.get_query_str() == "SELECT * FROM dim_ship LIMIT 10"


@pytest.mark.parametrize(
    "input_parameter,expected_operator",
    [("mid_in", "IN"), ("mid_nin", "NOT IN"),
     ("mid_gt", ">"), ("mid_gte", ">="),
     ("mid_lte", "<="), ("mid_lt", "<")]
)
def test_get_sql_operator(input_parameter, expected_operator):
    qb = QueryBuilder(SQL_PATH)
    assert qb.get_sql_operator(input_parameter) == expected_operator


@pytest.mark.parametrize(
    "input_param_error,expected_error",
    [("mid_in", does_not_raise()), ("mid_nin", does_not_raise()),
     ("mid_gt", does_not_raise()), ("mid_gte", does_not_raise()),
     ("mid_lte", does_not_raise()), ("mid_lt", does_not_raise()),
     ("mid_gtt", pytest.raises(Exception)), ("mid_gtee", pytest.raises(Exception)),
     ("mid", pytest.raises(Exception)), ("mid_", pytest.raises(Exception)),
     ]
)
def test_get_sql_operator_error(input_param_error, expected_error):
    qb = QueryBuilder(SQL_PATH)
    with expected_error:
        assert qb.get_sql_operator(input_param_error)
