from datetime import datetime, timedelta


def parse_date(date_string, timedelta=timedelta(days=0)):
    try:
        return (datetime.strptime(date_string, "%Y-%m-%d") + timedelta).timestamp()
    except ValueError:
        return None
