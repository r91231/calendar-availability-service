import os
import sys
import logging
from datetime import datetime, timedelta
from exceptions import CalendarAppException, RepositoryAccessError
from repositories.csv_calendar_repository import CsvCalendarRepository
from services.availability_service import AvailabilityService

logger = logging.getLogger(__name__)


def setup_logging():
    """Configures system-wide logging format and standard output handler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    setup_logging()
    logger.info("Starting Meeting Scheduling System...")

    try:
        # Dynamic absolute path resolution for calendar.csv
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "data", "calendar.csv")
        repository = CsvCalendarRepository(csv_path)
        service = AvailabilityService(repository)

        run_interactive_cli(service)

    except RepositoryAccessError as e:
        logger.error("Failed to access repository: %s", e)
        print(f"\n[Error] Could not load calendar data: {e}")
    except CalendarAppException as e:
        logger.error("Domain application error: %s", e)
        print(f"\n[Error] Application error: {e}")
    except Exception as e:
        logger.critical("Unexpected error occurred: %s", e, exc_info=True)
        print("\n[Critical] An unexpected error occurred. Please check the logs.")


def run_interactive_cli(service: AvailabilityService):
    """Runs the main command-line interface loop for users."""
    print("========================================")
    print("Welcome to the Calendar Scheduling CLI")
    print("========================================")

    while True:
        try:
            raw_input_persons = input("\nEnter participant names (comma-separated, or 'exit' to quit): ").strip()

            if raw_input_persons.lower() == 'exit':
                logger.info("User requested application exit.")
                print("Goodbye!")
                break

            if not raw_input_persons:
                print("Please enter at least one participant name.")
                continue

            person_list = [p.strip() for p in raw_input_persons.split(",") if p.strip()]

            raw_duration = input("Enter meeting duration in minutes (e.g., 30, 60): ").strip()
            if not raw_duration.isdigit() or int(raw_duration) <= 0:
                print("Invalid duration. Please enter a positive integer.")
                continue

            duration = timedelta(minutes=int(raw_duration))

            available_slots = service.find_available_slots(person_list, duration)

            print("\n----------------------------------------")
            if not available_slots:
                print("No available time slots found matching your criteria.")
                print("----------------------------------------")
                continue

            print(f"Available slots for {', '.join(person_list)}:")
            for index, slot in enumerate(available_slots, start=1):
                print(f" [{index}] {slot.strftime('%H:%M')}")
            print("----------------------------------------")

            # Capture user choice for booking
            choice = input("\nEnter the number of the slot you want to book (or press Enter to skip): ").strip()

            if choice.isdigit() and 1 <= int(choice) <= len(available_slots):
                selected_slot = available_slots[int(choice) - 1]
                event_name = input("Enter a title/name for the meeting: ").strip()

                if not event_name:
                    event_name = "Untitled Meeting"

                # Schedule and persist the meeting
                service.schedule_meeting(
                    person_list=person_list,
                    event_name=event_name,
                    start_time=selected_slot,
                    duration=duration
                )
                print(
                    f"\n[Success] Meeting '{event_name}' successfully scheduled and saved for {selected_slot.strftime('%H:%M')}!")
            else:
                print("No slot selected. Returning to main menu.")

        except CalendarAppException as e:
            logger.error("Error during execution: %s", e)
            print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()