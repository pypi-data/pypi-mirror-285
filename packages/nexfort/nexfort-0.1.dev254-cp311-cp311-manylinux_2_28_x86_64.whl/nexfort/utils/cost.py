import inspect
import time
from functools import wraps

from nexfort.utils.logging import logger

_time_cost_deepth = 1


class time_cost:
    """
    simple cost time code ranges using a decorator.
    """

    # TODO: debug need to be setted.
    def __init__(self, debug=0, message="\t"):
        import nexfort

        self._enable = nexfort._nexfort_debug_level >= debug
        self.message = message

    def __call__(self, func):
        @wraps(func)
        def clocked(*args, **kwargs):
            if not self._enable:
                return func(*args, **kwargs)
            global _time_cost_deepth
            module = inspect.getmodule(func)
            logger.vinfo1(f"{'==' * _time_cost_deepth}> function {module.__name__}.{func.__name__} try to run...")
            _time_cost_deepth += 1
            start_time = time.time()
            out = func(*args, **kwargs)
            end_time = time.time()
            _time_cost_deepth -= 1
            logger.vinfo1(
                f"<{'==' * _time_cost_deepth} function {module.__name__}.{func.__name__} finish run, cost {end_time - start_time} seconds"
            )
            return out

        return clocked
