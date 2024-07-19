from datetime import datetime, time
from enum import Enum


class TimeRange:
    def __init__(self, start: time, end: time) -> None:
        self.start = start
        self.end = end

    def __contains__(self, item):
        if isinstance(item, TimeRange):
            return self.start <= item.start <= self.end and self.start <= item.end <= self.end
        if isinstance(item, datetime):
            item = item.time()
        return self.start <= item <= self.end

    def __eq__(self, o: 'TimeRange') -> bool:
        return self.start == o.start and self.end == o.end

    def __repr__(self) -> str:
        return f'{self.start}-{self.end}'

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    @classmethod
    def from_str(cls, s: str) -> 'TimeRange':
        start, end = s.split('-')
        start = datetime.strptime(start.strip(), '%H:%M:%S').time()
        end = datetime.strptime(end.strip(), '%H:%M:%S').time()
        return cls(start, end)


class Frequency(Enum):
    hourly = 'hourly'
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'
    yearly = 'yearly'


if __name__ == '__main__':
    from time import sleep
    a = TimeRange.from_str('00:00:00 - 00:00:10')
    print(a)
    print(str(a))
    while True:
        print(datetime.now() in a)
        sleep(1)
