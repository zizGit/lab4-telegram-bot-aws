import io

from nure.schedule import read_outlook_calendar_csv


def test_schedule():
    f = open("nure/tests/TimeTable_20_12_2023 (1).csv", "br")
    decoded = f.read().decode("cp1251")
    events = read_outlook_calendar_csv(io.StringIO(decoded))

    assert len(events) > 0
