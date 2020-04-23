# -*- coding: utf-8 -*-
from typing import Union
from datetime import datetime, timedelta
from tpe_utils.dates import any_to_datetime
import math


def date_to_key(date: datetime) -> float:
    return date.timestamp()

Date = Union[int, float, datetime]
Numeric = Union[int, float]

def to_key(arg: Union[int, float, datetime]) -> Numeric:
    if isinstance(arg, (float, int)):
        return arg
    elif isinstance(arg, datetime):
        return date_to_key(arg)
    else:
        raise TypeError(
          f"'arg' must be one of (int, float, datetime) not '{type(arg)}'"
        )

class TimedContainer(dict):
    """

    """
    def __init__(self, *args, **kwargs):
        super(TimedContainer, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, (int, float)):
            key_ = key
        elif isinstance(key, datetime):
            key_ = date_to_key(key)
        else:
            raise TypeError(
              f"'key' must be one of (int, float, datetime) not '{type(key)}'"
            )
        dict.__setitem__(self, key_, value)

    def greater_than(self, bound: Date) -> "TimedContainer":
        return TimedContainer({k: v for k, v in self.items() if k > to_key(bound)})

    def less_than(self, bound: Date) -> "TimedContainer":
        return TimedContainer({k: v for k, v in self.items() if k < to_key(bound)})

    def between(self, lower_bound: Date, upper_bound: Date) -> "TimedContainer":
        return TimedContainer(
          {
              k: v
              for k, v in self.items()
              if to_key(lower_bound) < k < to_key(upper_bound)
          }
        )

    @property
    def to_list(self, sort=False, desc=False) -> list:
        if sort:
            keys = sorted(self.keys())
            if desc:
                keys.reverse()
            return [self[i] for i in keys]
        else:
            return list(self.values())

class TimedRing:
    """
    This is a storage container for any kind of object. This container merely stores
    the items in a dictionary with the keys being the timestamps that they were added.
    """

    container: dict

    def __init__(self, limit: int = 60):
        self.container = TimedContainer()
        self.limit = limit

    @property
    def oldest_key_allowed(self) -> int:
        now = datetime.utcnow() - timedelta(seconds=self.limit)
        return math.floor(now.timestamp())

    def prune_container(self) -> int:
        """
        Delete all keys from the container that are older than the oldest_key_allowed
        """
        oldest = self.oldest_key_allowed
        keys_to_delete = [k for k in self.container.keys() if k > oldest]
        for k in keys_to_delete:
            del self.container[k]
        return len(keys_to_delete)

    def add_item(self, item, date: Date = None):
        if date is not None:
            if isinstance(date, datetime):
                date_ = date_to_key(date)
            else:
                date_ = date_to_key(any_to_datetime(date))
        else:
            date_ = date_to_key(datetime.utcnow())
        self.container[date_] = item

    def get_n_seconds(self, seconds: int) -> list:
        get_newer_than = (datetime.utcnow() - timedelta(seconds=seconds)).timestamp()
        keys_to_return = [k for k in self.container.keys()]
        return [self.container[k] for k in keys_to_return]
