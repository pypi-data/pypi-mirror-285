from typing import Optional

class RetryException(Exception):
    def __init__(self, delay: Optional[int]):
        self.delay = delay

class AbortException(Exception):
    pass
