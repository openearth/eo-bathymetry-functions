from eo_bathymetry_functions.utils import get_rolling_window_dates

def test_get_rolling_window_dates():
    dates = get_rolling_window_dates("2018-01-01", "2020-04-01")
    assert dates == [
        ("2018-01-01", "2020-01-01"), ("2018-04-01", "2020-04-01")]