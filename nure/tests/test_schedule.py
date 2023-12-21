import io

from nure.schedule import read_outlook_calendar_csv


def test_schedule():
    f = open("nure/tests/TimeTable_20_12_2023 (1).csv", "r", encoding="cp1251")
    events = read_outlook_calendar_csv(f)

    assert len(events) > 0
    assert events[0].title == "*Clpr Лк ФІЛІЯ КІУКІ-20-7,8,9"
