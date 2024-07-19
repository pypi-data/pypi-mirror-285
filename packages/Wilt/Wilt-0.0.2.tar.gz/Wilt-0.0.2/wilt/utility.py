import itertools
from datetime import datetime
from typing import Iterable, Iterator, TypeVar


T = TypeVar('T')
K = TypeVar('K')


def chunk_iter(iterable: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, k))
        if not chunk:
            break
        yield chunk


def partition_pair_iter(
    iterable: Iterable[tuple[K, T]], k: int
) -> Iterable[tuple[K, tuple[T, ...]]]:
    buffer = {}
    for key, value in iterable:
        if key not in buffer:
            buffer[key] = []

        buffer[key].append(value)

        if len(buffer[key]) == k:
            yield key, tuple(buffer[key])
            buffer[key].clear()

    for key, values in buffer.items():
        if values:
            yield key, tuple(values)


def parse_timestamp(s: str) -> datetime:
    if s.endswith('Z'):
        s = s.replace('Z', '+00:00')

    return datetime.fromisoformat(s)


class CommandError(Exception):
    """Generic command error."""
