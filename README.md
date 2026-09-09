# calendar-availability-service
A Python-based meeting scheduling application designed to calculate shared availability among multiple participants, process calendar entries from CSV storage, and book new events with automated persistence and sorting.

---

## 🌳 Project Directory Tree

```text
python-project/
│
├── data/
│   └── calendar.csv
│
├── models/
│   ├── __init__.py
│   ├── event.py
│   └── time_interval.py
│
├── repositories/
│   ├── __init__.py
│   ├── calendar_repository.py
│   └── csv_calendar_repository.py
│
├── services/
│   ├── __init__.py
│   └── availability_service.py
│
├── io_comp/
│   ├── __init__.py
│   └── app.py
│
├── exceptions.py
├── setup.py
└── README.md

Overview & Benefits
Why is this system useful?
Coordinating meetings across multiple team members or participants often leads to complex, back-and-forth communication. This application automates the resolution of schedule overlaps by mathematically calculating common free time windows across all requested participants.

Key Advantages
Automatic Overlap Merging: Consolidates overlapping occupied intervals in O(n log n) time complexity to determine true continuous availability.

Dynamic Participant Handling: Treats unknown or newly added participants as fully available across working hours (07:00–19:00) without throwing system errors.

Automated Data Persistence: Saves newly booked events directly to CSV storage, maintaining chronological and alphabetical ordering automatically.

Robust Logging: Integrates structured system-level logging for seamless debugging and monitoring.

📄 File Details & Function Reference
1. exceptions.py
Defines domain-specific custom exception classes for standardizing error handling across the layers.

CalendarAppException: Base exception class for all custom domain errors.

ParticipantNotFoundError: Exception raised when a requested person is not present in the repository (retained for explicit validation cases).

InvalidTimeIntervalError: Exception raised when a TimeInterval is instantiated with a start time greater than or equal to its end time.

RepositoryAccessError: Exception raised when reading, parsing, or writing to the CSV backing store fails.

2. models/event.py
Defines the core data model representing an individual calendar entry.

Event (Dataclass): Immutable structure storing event attributes:

person_name: The participant assigned to the event.

event_name: The title/description of the event.

start_time: Datetime object for event start.

end_time: Datetime object for event end.

3. models/time_interval.py
Defines time-bound ranges used in availability calculations.

TimeInterval (Dataclass): Represents a continuous span between start_time and end_time.

__post_init__(): Validation hook that enforces start_time < end_time upon instantiation, raising InvalidTimeIntervalError on violation.

4. repositories/calendar_repository.py
Defines the abstract interface contract for repository implementations.

CalendarRepository (Interface/Protocol):

get_events(): Abstract method returning a list of Event objects.

add_event(new_event): Abstract method defining contract for persisting a new event.

5. repositories/csv_calendar_repository.py
Concrete repository implementation handling file I/O operations against CSV storage.

CsvCalendarRepository:

__init__(file_path): Initializes repository with the absolute or relative CSV target path.

_parse_datetime(time_str): Private helper converting ISO strings or HH:MM time strings into valid datetime objects.

get_events(): Reads the CSV file, detects header presence automatically, parses all rows into Event models, and returns them.

add_event(new_event): Appends a new event, sorts the master dataset alphabetically by person_name and chronologically by start_time, and rewrites the CSV file safely.

6. services/availability_service.py
Contains business logic for overlap detection, slot computation, and meeting scheduling.

AvailabilityService:

__init__(calendar_repository): Injects the repository instance dependency.

find_available_slots(person_list, event_duration): Public service interface that coordinates filtering, interval merging, and available slot calculations for participants.

schedule_meeting(person_list, event_name, start_time, duration): Creates and persists new Event records for each participant across the requested duration.

_get_events_for_persons(person_list): Filters stored events by participant list and logs instances of unrecognized participants.

_merge_events(events): Consolidates overlapping and adjacent occupied event intervals into unified TimeInterval objects.

_calculate_free_slots(merged_intervals, duration): Scans non-occupied windows between 07:00 and 19:00 to generate valid starting times matching the requested meeting duration.

7. io_comp/app.py
Presentation layer executing the user interface and setting up core runtime configs.

setup_logging(): Configures root logger handlers, output formatting, and log severity levels (INFO standard).

main(): Initializes dependencies using relative path resolution for data/calendar.csv and starts the application CLI loop.

run_interactive_cli(service): Manages interactive prompt loops for capturing participant queries, displaying available meeting slots, reading booking selections, and triggering schedule creation.
