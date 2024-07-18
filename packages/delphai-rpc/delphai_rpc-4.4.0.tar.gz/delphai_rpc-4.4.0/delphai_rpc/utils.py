import datetime
import functools
import re

from typing import Callable


def fix_message_timestamp(func: Callable) -> Callable:
    @functools.wraps(func)
    def inner(message):
        # Fix `pamqp` naive timestamp
        if message.timestamp:
            message.timestamp = message.timestamp.replace(tzinfo=datetime.timezone.utc)

        return func(message)

    return inner


def clean_service_name(service_name: str) -> str:
    return re.sub("[^a-z0-9-]+", "-", service_name.strip().lower())
