import pytest
from app.routers.v1.ship.router import update_params_datetime
import datetime

dates = [
    ("2021-01-01T00:00:00Z", "from", 20210101, 0, "from_date", "from_time"),
    ("2021-01-01T00:00:00Z", "to", 20210101, 0, "to_date", "to_time"),
    ("2019-02-11T00:00:40Z", "from", 20190211, 40, "from_date", "from_time"),
    ("2019-02-11T00:00:40Z", "to", 20190211, 40, "to_date", "to_time"),
    ("2021-06-05T00:22:01Z", "from", 20210605, 2201, "from_date", "from_time"),
    ("2021-06-05T00:22:01Z", "to", 20210605, 2201, "to_date", "to_time"),
    ("2020-12-26T12:22:06Z", "from", 20201226, 122206, "from_date", "from_time"),
    ("2020-12-26T12:22:06Z", "to", 20201226, 122206, "to_date", "to_time"),
]

@pytest.mark.parametrize("datetime_input, from_or_to, exp_date, exp_time, date_key, time_key", dates)
def test_update_params_datetime(datetime_input, from_or_to, exp_date, exp_time, date_key, time_key):
    params = {}
    datetime_input = datetime.datetime.fromisoformat(datetime_input)
    update_params_datetime(params, datetime_input, from_or_to)
    assert params == {date_key: exp_date, time_key: exp_time}
