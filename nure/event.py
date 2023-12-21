from dataclasses import dataclass


@dataclass
class Event:
    title: str
    start_date: str
    start_time: str
    end_date: str
    end_time: str
