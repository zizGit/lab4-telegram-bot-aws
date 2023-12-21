import boto3

from nure.event import Event

sdb = boto3.client("sdb")


def delete_schedule(schedule_id: str) -> None:
    sdb.delete_domain(DomainName=schedule_id)


def create_schedule(schedule_id: str) -> None:
    sdb.create_domain(DomainName=schedule_id)


def split_list(lst, chunk_size):
    """Splits a list into chunks of specified size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def put_schedule(schedule_id: str, events: list[Event]) -> None:
    for chunk in split_list(events, 25):
        sdb.batch_put_attributes(
            DomainName=schedule_id,
            Items=[
                {
                    "Name": event.start_date
                    + " "
                    + event.start_time
                    + " "
                    + event.title,
                    "Attributes": [
                        {"Name": "title", "Value": event.title},
                        {"Name": "start_date", "Value": event.start_date},
                        {"Name": "start_time", "Value": event.start_time},
                        {"Name": "end_date", "Value": event.end_date},
                        {"Name": "end_time", "Value": event.end_time},
                    ],
                }
                for event in chunk
            ],
        )


def select(schedule_id: str, start_date: str) -> list[Event]:
    result = sdb.select(
        SelectExpression=f"select * from {schedule_id} where start_date = '{start_date}'"
    )

    items = result.get("Items", [])

    events: list[Event] = []

    for item in items:
        attrs = item["Attributes"]
        kwargs = {attr["Name"]: attr["Value"] for attr in attrs}
        events.append(Event(**kwargs))

    return sorted(events, key=lambda e: e.start_time)
