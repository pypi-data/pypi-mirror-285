import math
from typing import Any

class Epsilon():
    def __init__(self, f, **kwargs) -> None:
        self.f = f
        self.kwargs = kwargs
        self.steps_done = 0
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        result = self.f(self.steps_done, **self.kwargs)
        self.steps_done += 1
        return result
        

"""
Functions in this file return the epsilon threshold at a specific step. They should be called as 
f(steps_done, *args)
"""

def exp_decrease(steps_done, start, end, steps_to_end):
    return end + (start - end) * math.exp(-1. * steps_done / steps_to_end)


def lin_decrease(steps_done, start, end, steps_to_end):
    progress = (steps_done / steps_to_end)
    return start + (end - start) * (progress if progress <= 1 else 1.0)