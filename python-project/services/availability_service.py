import logging
from datetime import datetime, timedelta, time
from models.event import Event
from models.time_interval import TimeInterval
from repositories.calendar_repository import CalendarRepository

logger = logging.getLogger(__name__)


class AvailabilityService:
    def __init__(self, calendar_repository: CalendarRepository):
        self._calendar_repository = calendar_repository

    def find_available_slots(
            self,
            person_list: list[str],
            event_duration: timedelta
    ) -> list[datetime]:
        """
        Finds common available time slots for all specified participants.
        If a participant is not found in the repository, they are treated as having full availability.
        """
        logger.info("Searching available slots for participants: %s", person_list)

        # Early Exit optimization
        if not person_list:
            logger.warning("Empty participant list provided. Returning empty slots.")
            return []

        relevant_events = self._get_events_for_persons(person_list)
        logger.debug("Retrieved %d relevant events for specified participants", len(relevant_events))

        merged_intervals = self._merge_events(relevant_events)
        available_slots = self._calculate_free_slots(merged_intervals, event_duration)

        logger.info("Found %d available slots", len(available_slots))
        return available_slots

    def schedule_meeting(
            self,
            person_list: list[str],
            event_name: str,
            start_time: datetime,
            duration: timedelta
    ) -> None:
        """
        Schedules a new meeting for all specified participants and persists it to storage.
        """
        end_time = start_time + duration

        for person in person_list:
            new_event = Event(
                person_name=person,
                event_name=event_name,
                start_time=start_time,
                end_time=end_time
            )
            self._calendar_repository.add_event(new_event)
            logger.info("Scheduled new event '%s' for %s from %s to %s", event_name, person, start_time, end_time)

    def _get_events_for_persons(self, person_list: list[str]) -> list[Event]:
        all_events = self._calendar_repository.get_events()
        existing_participants = {event.person_name for event in all_events}

        for person in person_list:
            if person not in existing_participants:
                logger.info(
                    "Participant '%s' not found in repository. Treating as new participant with full availability.",
                    person
                )

        return [e for e in all_events if e.person_name in person_list]

    def _merge_events(self, events: list[Event]) -> list[TimeInterval]:
        """
        Merges overlapping or contiguous events into a consolidated list of TimeIntervals.
        """
        if not events:
            return []

        intervals = [
            TimeInterval(event.start_time, event.end_time)
            for event in events
        ]

        intervals.sort(key=lambda interval: interval.start_time)
        merged_intervals = [intervals[0]]

        for interval in intervals[1:]:
            last_interval = merged_intervals[-1]

            if interval.start_time <= last_interval.end_time:
                merged_intervals[-1] = TimeInterval(
                    start_time=last_interval.start_time,
                    end_time=max(last_interval.end_time, interval.end_time)
                )
            else:
                merged_intervals.append(interval)

        return merged_intervals

    def _calculate_free_slots(self, merged_intervals: list[TimeInterval], duration: timedelta) -> list[datetime]:
        """
        Calculates free time slots within workday hours (07:00 to 19:00).
        """
        base_date = merged_intervals[0].start_time.date() if merged_intervals else datetime.now().date()
        workday_start = datetime.combine(base_date, time(7, 0))
        workday_end = datetime.combine(base_date, time(19, 0))

        if not merged_intervals:
            free_slots = []
            current_time = workday_start
            while current_time + duration <= workday_end:
                free_slots.append(current_time)
                current_time += duration
            return free_slots

        free_slots = []
        current_time = workday_start

        for interval in merged_intervals:
            int_start = max(interval.start_time, workday_start)
            int_end = min(interval.end_time, workday_end)

            while current_time + duration <= int_start:
                free_slots.append(current_time)
                current_time += duration

            if current_time < int_end:
                current_time = int_end

        while current_time + duration <= workday_end:
            free_slots.append(current_time)
            current_time += duration

        return free_slots