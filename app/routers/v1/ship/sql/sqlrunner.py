import os

def get_sql_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)

def get_sql_file_contents(file_name):
    with open(get_sql_file_path(file_name), 'r') as f:
        return f.read()

def run_sql_file(file_name, dw):
    return dw.execute(get_sql_file_contents(file_name))

def run_sql_file_with_params(file_name, dw, params):
    return dw.execute(get_sql_file_contents(file_name), params)