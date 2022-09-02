import pytest

from eo_bathymetry_functions.utils import get_rolling_window_dates

def test_get_rolling_window_dates_2periods():
    dates = get_rolling_window_dates("2018-01-01", "2020-04-01")
    assert dates == [
        ("2018-01-01", "2020-01-01"), ("2018-04-01", "2020-04-01")]

def test_get_rolling_window_dates_periods_too_close():
    with pytest.raises(RuntimeError):
        get_rolling_window_dates("2015-01-01", "2016-01-01")

def test_get_rolling_window_dates_start_stop_reversed():
    with pytest.raises(RuntimeError):
        dates = get_rolling_window_dates("2020-04-01", "2018-01-01")