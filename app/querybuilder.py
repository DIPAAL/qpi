"""Module for the query builder class."""
from sqlalchemy import text
from helper_functions import get_file_contents
import os


class QueryBuilder:
    """A class to build a query from a set of sql files and/or strings."""

    def __init__(self, sql_path):
        """
        Initialise the query builder.

        Args:
            sql_path: The path to the folder containing the sql files
        """
        self.sql_path = sql_path
        self.query = ""

    def add_sql(self, sql_file, new_line=True):
        """
        Add the contents of a sql file to the query.

        Args:
            sql_file: The name of the sql file to add to the query
            new_line: Whether to add a new line before the sql files content in added to the query
        """
        if not sql_file.endswith(".sql"):
            raise ValueError("File must be a .sql file")
        if new_line:
            self.query += "\n"
        self.query += get_file_contents(os.path.join(self.sql_path, sql_file))

    def add_string(self, string, new_line=True):
        """
        Add a string to the query.

        Args:
            string: The string to add to the query
            new_line: Whether to add a new line before the string is added to the query
        """
        if new_line:
            self.query += "\n"
        self.query += string

    def add_sql_with_replace(self, sql_file, replace: dict, new_line=True):
        """
        Add the contents of a sql file to the query, replacing the keys in the replace dict with the values.

        Args:
            sql_file: The name of the sql file to add to the query
            replace: A dict with keys to replace in the sql file and the values to replace them with
            new_line: Whether to add a new line before the sql files content in added to the query
        """
        if new_line:
            self.query += "\n"
        file = get_file_contents(os.path.join(self.sql_path, sql_file))

        for key, value in replace.items():
            file = file.replace(key, value)

        self.query += file

    def add_where(self, param, operator, value, new_line=True):
        """
        Add a where clause to the query.

        Args:
            param: What parameter to filter on
            operator: What operator to use in the where clause.
            value: What value to filter on
            new_line: Whether to add a new line before the where clause is added to the query
        """
        if new_line:
            self.query += "\n"

        value = self._convert_value(value)

        if "WHERE" in self.query:
            self.query += f"AND {param} {operator} {value}"
        else:
            self.query += f"WHERE {param} {operator} {value}"

    def _convert_value(self, value):
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

    def remove_query(self):
        """Remove all content from the query string."""
        self.query = ""

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

    def write_query_to_file(self, file_path, file_name):
        """
        Write the query to a file.

        Args:
            file_path: The path to the file
            file_name: The name of the file
        """
        with open(os.path.join(file_path, file_name), "w") as file:
            file.write(self.query)


def get_sql_operator(param_name):
    """Get the sql operator from the parameter name.

    Args:
        param_name: The name of the parameter to get the operator from

    Returns:
        The sql operator as a string
    """
    operators_l3 = {"_in": "IN", "_gt": ">", "_lt": "<"}
    operators_l4 = {"_nin": "NOT IN", "_gte": ">=", "_lte": "<="}

    for key, value in operators_l3.items():
        if key in param_name[-3:]:
            return value
    for key, value in operators_l4.items():
        if key in param_name[-4:]:
            return value

    raise ValueError("Invalid type of parameter")
