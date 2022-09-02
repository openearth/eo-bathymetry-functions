from datetime import date as Date, datetime, timedelta
from os import environ
from typing import Dict, List, Optional, Tuple

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from flask import Request


PROJECT = environ.get("PROJECT")

def set_up_cf_logging(request: Request) -> Dict[str, str]:
    """
    set up logging for a google cloud function
    """

    global_log_fields: Dict[str, str] = {}
    trace_header: str = request.headers.get("X-Cloud-Trace-Context")
    if trace_header and PROJECT:
        trace = trace_header.split("/")
        global_log_fields["logging.googleapis.com/trace"] = f"projects/{PROJECT}/traces/{trace[0]}"
    
    return global_log_fields

def get_rolling_window_dates(
    start: Optional[str] = None,
    stop: Optional[str] = None,
    step_months: int = 3,
    window_years: int = 2
    ) -> List[Tuple[Date]]:
    if not stop:
        now: datetime = datetime.now()
        stop: datetime = datetime(year=now.year, month=now.month, day=1)
    else:
        stop: datetime = parse(stop)
    
    # Make sure that an undefined start call takes one timestep for processing
    if not start:
        start = stop - relativedelta(years=window_years)  # - relativedelta(months=step_months)
    else:
        start: datetime = parse(start)

    def rolling_time_window(start: Date, stop: Date, dt: relativedelta, window_length: relativedelta) -> List[Tuple[Date]]:
        if stop - window_length - start < timedelta(0):
            raise RuntimeError("Stop and Start too close")
        
        window_list: List[Tuple[Date]] = []
        t: Date = start
        while t <= stop - window_length:
            window_list.append((str(t), str(t+window_length)))
            t += dt
        return window_list
    
    start_date: Date = Date(year=start.year, month=start.month, day=start.day)
    stop_date: Date = Date(year=stop.year, month=stop.month, day=stop.day)
    return rolling_time_window(start_date, stop_date, relativedelta(months=step_months), relativedelta(years=window_years))
