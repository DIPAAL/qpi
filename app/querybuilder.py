"""Module for the query builder class."""
from sqlalchemy import text
from helper_functions import get_file_contents
import os
from typing import Any


class QueryBuilder:
    """A class to build a query from a set of sql files and/or strings."""

    def __init__(self, sql_path: str):
        """
        Initialise the query builder.

        Args:
            sql_path (str): The path to the directory containing the sql files
        """
        self.sql_path = sql_path
        self.query = ""

    def add_sql(self, sql_file: str, new_line=True):
        """
        Add the contents of a sql file to the query.

        Args:
            sql_file (str): The name of the sql file to add to the query
            new_line (bool): Whether to add a new line before the sql file's content is added to the query
        """
        if not sql_file.endswith(".sql"):
            raise ValueError("File must be a .sql file")

        if new_line:
            self.query += "\n"

        self.query += get_file_contents(os.path.join(self.sql_path, sql_file))
        return self

    def add_string(self, string: str, new_line=True):
        """
        Add a string to the query.

        Args:
            string (str): The string to add to the query
            new_line (bool): Whether to add a new line before the string is added to the query
        """
        if new_line:
            self.query += "\n"

        self.query += string
        return self

    def add_sql_with_replace(self, sql_file: str, replace: dict, new_line=True):
        """
        Add the contents of a sql file to the query, replacing the keys in the replace dict with the values.

        Args:
            sql_file (str): The name of the sql file to add to the query
            replace (dict): A dict with keys representing the strings to replace and
                values representing the strings to replace them with
            new_line (bool): Whether to add a new line before the sql file's content is added to the query
        """
        if new_line:
            self.query += "\n"
        file = get_file_contents(os.path.join(self.sql_path, sql_file))

        file = file.format(**replace)

        self.query += file
        return self

    def add_where(self, param: str, operator: str, value: Any, new_line=True):
        """
        Add a where clause to the query.

        Args:
            param (str): What parameter to filter on
            operator (str): What operator to use in the where clause.
            value (Any): What value to filter on
            new_line (bool): Whether to add a new line before the where clause is added to the query
        """
        if new_line:
            self.query += "\n"

        value = self._convert_value(value)

        if "WHERE" in self.query:
            self.query += f"AND {param} {operator} {value}"
        else:
            self.query += f"WHERE {param} {operator} {value}"
        return self

    @staticmethod
    def _convert_value(value: Any):
        """Convert a value to a format that can be used in a query."""
        if isinstance(value, list):
            # This is to prevent the query from breaking if the list only contains one value
            if len(value) == 1:
                if isinstance(value[0], str):
                    value = f"('{value[0]}')"
                else:
                    value = f"({value[0]})"
            # This is to convert a list to a tuple as SQL does not support lists
            else:
                value = tuple(value)
        return value

    def end_query(self):
        """Add a semicolon to the end of the query."""
        self.query += ";"  # Add semicolon to end of query

    def get_query_text(self):
        """
        Get the query as a sqlalchemy text object.

        Returns: The query as textual SQL
        """
        return text(self.query)

    def get_query_str(self):
        """
        Get the query as a string.

        Returns: The query as string
        """
        return self.query

    def write_query_to_file(self, file_path: str, file_name: str):
        """
        Write the query to a file.

        Args:
            file_path (str): The path to the file
            file_name (str): The name of the file
        """
        with open(os.path.join(file_path, file_name + ".sql"), "w") as file:
            file.write(self.query)

    @staticmethod
    def get_sql_operator(param_name: str):
        """Get the sql operator from the parameter name.

        Args:
            param_name (str): The name of the parameter to get the operator from

        Returns:
            The sql operator as a string
        """
        operators = {"_in": "IN", "_gt": ">", "_lt": "<", "_nin": "NOT IN", "_gte": ">=", "_lte": "<="}
        key_start_idx = param_name.rfind('_')
        try:
            return operators[param_name[key_start_idx:]]
        except KeyError:
            raise ValueError("Invalid type of parameter")
