from pydantic import BaseModel

class CountRows(BaseModel):
    count: int = 234

class ColumnNames(BaseModel):
    columns: list[str] = [ "time", "time_id", "hour_of_day", "minute_of_hour", "second_of_minute"]