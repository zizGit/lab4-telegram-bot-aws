import csv
import io

from nure.event import Event


def read_outlook_calendar_csv(obj) -> list[Event]:
    events: list[Event] = []
    reader = csv.DictReader(obj)
    for r in reader:
        events.append(
            Event(
                title=r["Тема"],
                start_date=r["Дата начала"],
                start_time=r["Время начала"],
                end_date=r["Дата завершения"],
                end_time=r["Время завершения"],
            )
        )
    return events
