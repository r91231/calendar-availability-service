from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Event:
    person_name: str
    event_name: str
    start_time: datetime
    end_time: datetime