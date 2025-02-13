from typing import Optional, Dict, Any
import pandas as pd
from functools import wraps

def query(sql_file: str):
    """Decorator to mark methods as queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get the params from the function
            params = func(self, *args, **kwargs)
            # Execute the query
            raw_results = self._db._inject_and_execute_sql(sql_file, params)
            # Process the results if a process_results method exists
            process_method = f"_process_{func.__name__}"
            if hasattr(self, process_method):
                return getattr(self, process_method)(raw_results)
            return raw_results
        return wrapper
    return decorator

