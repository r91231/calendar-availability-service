from datetime import time, timedelta, datetime
from models.event import Event
from repositories.calendar_repository import CalendarRepository
from services.availability_service import AvailabilityService


class MockCalendarRepository(CalendarRepository):
    def __init__(self, events: list[Event]):
        self._events = events

    def get_events(self) -> list[Event]:
        return self._events


def test_overlapping_events_merged_correctly():
    # מקרה שבו אירועים חופפים של אנשים שונים מתמזגים
    events = [
        Event("Alice", "Meeting 1", datetime.strptime("08:00", "%H:%M"), datetime.strptime("09:00", "%H:%M")),
        Event("Jack", "Meeting 2", datetime.strptime("08:30", "%H:%M"), datetime.strptime("10:00", "%H:%M"))
    ]
    repo = MockCalendarRepository(events)
    service = AvailabilityService(repo)

    # נחפש חלון של שעה עבור Alice ו-Jack
    slots = service.find_available_slots(["Alice", "Jack"], timedelta(hours=1))

    # הטווח 08:00 עד 10:00 תפוס, לכן החלון הראשון הפנוי בבוקר הוא 07:00 עד 08:00
    # והחלון הבא אחרי החפיפה הוא ב-10:00
    assert time(7, 0) in slots
    assert time(8, 0) not in slots
    assert time(8, 30) not in slots
    assert time(10, 0) in slots


def test_no_events_returns_all_slots():
    # מקרה שבו אין אירועים כלל - כל היום פנוי
    repo = MockCalendarRepository([])
    service = AvailabilityService(repo)

    slots = service.find_available_slots(["Alice"], timedelta(hours=1))

    # אמורים לקבל את כל השעות מ-07:00 עד 18:00
    assert slots[0] == time(7, 0)
    assert time(18, 0) in slots
    assert len(slots) == 12