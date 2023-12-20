from nure.schedule import read_outlook_calendar_csv_from_file


def test_schedule():
    read_outlook_calendar_csv_from_file("nure/tests/TimeTable_20_12_2023 (1).csv")
