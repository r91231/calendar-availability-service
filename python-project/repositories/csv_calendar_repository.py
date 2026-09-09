import csv
import logging
from datetime import datetime, time
from models.event import Event
from repositories.calendar_repository import CalendarRepository
from exceptions import RepositoryAccessError

logger = logging.getLogger(__name__)


class CsvCalendarRepository(CalendarRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _parse_datetime(self, time_str: str) -> datetime:
        """
        Parses ISO datetime strings or falls back to combining today's date
        with HH:MM time strings.
        """
        time_str = time_str.strip()
        try:
            return datetime.fromisoformat(time_str)
        except ValueError:
            parsed_time = time.fromisoformat(time_str)
            return datetime.combine(datetime.now().date(), parsed_time)

    def get_events(self) -> list[Event]:
        """
        Reads events from the CSV file. Handles missing headers and time-only format.
        """
        events = []
        expected_headers = ['person_name', 'event_name', 'start_time', 'end_time']

        try:
            with open(self.file_path, mode='r', encoding='utf-8-sig') as file:
                sample = file.read(2048)
                file.seek(0)

                has_header = csv.Sniffer().has_header(sample) if sample else True

                if has_header:
                    reader = csv.DictReader(file)
                else:
                    reader = csv.DictReader(file, fieldnames=expected_headers)

                for row in reader:
                    events.append(
                        Event(
                            person_name=row['person_name'].strip(),
                            event_name=row['event_name'].strip(),
                            start_time=self._parse_datetime(row['start_time']),
                            end_time=self._parse_datetime(row['end_time'])
                        )
                    )
            logger.debug("Successfully loaded %d events from %s", len(events), self.file_path)
            return events
        except Exception as e:
            logger.error("Error reading CSV file %s: %s", self.file_path, e)
            raise RepositoryAccessError(f"Failed to read CSV repository: {e}")

    def add_event(self, new_event: Event) -> None:
        """
        Adds a new event, sorts all events first by person_name and then by start_time,
        and persists them back to CSV.
        """
        events = self.get_events()
        events.append(new_event)

        # Sort events primarily by person_name (alphabetically) and secondarily by start_time
        events.sort(key=lambda event: (event.person_name.lower(), event.start_time))

        try:
            with open(self.file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                fieldnames = ['person_name', 'event_name', 'start_time', 'end_time']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                for event in events:
                    writer.writerow({
                        'person_name': event.person_name,
                        'event_name': event.event_name,
                        'start_time': event.start_time.strftime('%H:%M'),
                        'end_time': event.end_time.strftime('%H:%M')
                    })
            logger.info("Successfully added event '%s' and saved sorted data to CSV", new_event.event_name)
        except Exception as e:
            logger.error("Error writing to CSV file %s: %s", self.file_path, e)
            raise RepositoryAccessError(f"Failed to write to CSV repository: {e}")