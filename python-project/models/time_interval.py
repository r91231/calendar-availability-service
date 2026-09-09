from dataclasses import dataclass
from datetime import datetime
from exceptions import InvalidTimeIntervalError

@dataclass(frozen=True)
class TimeInterval:
    start_time: datetime
    end_time: datetime

    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise InvalidTimeIntervalError("start_time must be earlier than end_time")