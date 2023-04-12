"""Module for the query builder class."""
from sqlalchemy import text
from helper_functions import get_file_contents
import os
from typing import Any
import numbers


class QueryBuilder:
    """A class to build a query from a set of sql files and/or strings."""

    def __init__(self, sql_path: str):
        """
        Initialise the query builder.

        Args:
            sql_path (str): The path to the directory containing the sql files
        """
        self.sql_path = sql_path
        self.inc_num = 0
        self.query = ""

    def add_sql(self, sql_file: str, new_line=True):
        """
        Add the contents of a sql file to the query.

        Args:
            sql_file (str): The name of the sql file to add to the query
            new_line (bool): Whether to add a new line before the sql file's content is added to the query
        """
        self._is_sql_file(sql_file)

        if new_line:
            self.query += "\n"

        self.query += get_file_contents(os.path.join(self.sql_path, sql_file))
        return self

    @staticmethod
    def _is_sql_file(file: str):
        """Check if a file is a sql file."""
        if not file.endswith(".sql"):
            raise ValueError("File must be a .sql file")

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

    def add_where(self, param_name: str, operator: str, value: Any, param_dict: dict = None, new_line=True):
        """
        Add a where clause to the query and add the parameter and its value to the param_dict if it is provided.

        Args:
            param (str): What parameter to filter on
            operator (str): What operator to use in the where clause.
            value (Any): What value to filter on
            param_dict (dict): The dict to add the parameter and its value to
            param_name (str): The name of the parameter to add to the dict
            new_line (bool): Whether to add a new line before the where clause is added to the query
        """
        if new_line:
            self.query += "\n"

        # If the value is a number, then we can trust it is a valid value
        if isinstance(value, numbers.Number):
            self._prefix_where_or_and(f"{param_name} {operator} {value}")

        if not param_dict:
            raise ValueError("param_dict must be provided if value is not an int")

        # If the value is not a number, then we must create placeholders for the value
        # This is to prevent SQL injection
        value_placeholder = f"{'param' + str(self.inc_num)}"
        self.inc_num += 1
        self._prefix_where_or_and(f"{param_name} {operator} :{value_placeholder}")

        if isinstance(value, list):
            value = tuple(value)

        local_dict = {value_placeholder: value}
        param_dict.update(local_dict)
        return self

    def add_where_from_file(self, sql_file, new_line=True):
        """
        Add a where clause from a file to the query.

        Args:
            sql_file (str): The name of the sql file to add to the query
            new_line (bool): Whether to add a new line before the where clause is added to the query
        """
        if new_line:
            self.query += "\n"

        self._prefix_where_or_and(get_file_contents(os.path.join(self.sql_path, sql_file)))

        return self

    def add_where_from_string(self, string, new_line=True):
        """
        Add a where clause from a string to the query.

        Args:
            string (str): The string to add to the query
            new_line (bool): Whether to add a new line before the where clause is added to the query
        """
        if new_line:
            self.query += "\n"

        self._prefix_where_or_and(string)

        return self

    def _prefix_where_or_and(self, string: str):
        """Check if the query already has a where clause."""
        self.query += f"AND {string}" if "WHERE" in self.query else f"WHERE {string}"

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

    def format_query(self, param_dict: dict):
        """Format the placeholders in the query with the values in the param_dict.

        Args:
            param_dict (dict): The dict containing the values to format the placeholders with
        """
        self.query = self.query.format(**param_dict)
