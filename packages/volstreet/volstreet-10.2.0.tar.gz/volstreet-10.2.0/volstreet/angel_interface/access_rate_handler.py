import time
import abc
import asyncio
from time import sleep


class StorageBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_token_count(self, key):
        pass

    @abc.abstractmethod
    def replenish(self, key, rate, capacity):
        pass

    @abc.abstractmethod
    def consume(self, key, num_tokens):
        pass


class MemoryStorage(StorageBase):

    def __init__(self):
        self._buckets = {}

    def get_token_count(self, key):
        try:
            return self._buckets[key][0]
        except KeyError:
            pass

        return 0

    def replenish(self, key, rate, capacity):

        try:
            tokens_in_bucket, last_replenished_at, last_consumed_at = self._buckets[key]
            now = time.monotonic()

            # To handle race conditions
            if now < last_replenished_at:
                return

            # If the bucket is empty and replenishment is not possible, return.
            if self._buckets[key][0] < 1 and now - last_consumed_at < 1.15:
                return

            # Replenish the bucket based on the rate and the time that has
            # passed since the last replenishment.
            self._buckets[key][0] = min(
                capacity, tokens_in_bucket + (rate * (now - last_consumed_at))
            )

            # Update the last replenished timestamp.
            self._buckets[key][1] = now

        except KeyError:
            self._buckets[key] = [capacity, time.monotonic(), time.monotonic() - 1.15]

    def consume(self, key, num_tokens):
        """Attempt to take one or more tokens from a bucket.

        This method is exposed for use by the token_bucket.Limiter
        class.
        """
        tokens_in_bucket = self._buckets[key][0]
        if tokens_in_bucket < num_tokens:
            return False

        self._buckets[key][0] -= num_tokens
        self._buckets[key][2] = time.monotonic()
        return True


class Limiter(object):

    __slots__ = (
        "_rate",
        "_capacity",
        "_storage",
    )

    def __init__(self, rate, capacity, storage):
        if not isinstance(rate, (float, int)):
            raise TypeError("rate must be an int or float")

        if rate <= 0:
            raise ValueError("rate must be > 0")

        if not isinstance(capacity, int):
            raise TypeError("capacity must be an int")

        if capacity < 1:
            raise ValueError("capacity must be >= 1")

        if not isinstance(storage, StorageBase):
            raise TypeError("storage must be a subclass of StorageBase")

        self._rate = rate
        self._capacity = capacity
        self._storage = storage

    def consume(self, key, num_tokens=1):

        if not key:
            if key is None:
                raise TypeError("key may not be None")

            raise ValueError("key must not be a non-empty string or bytestring")

        if num_tokens is None:
            raise TypeError("num_tokens may not be None")

        if num_tokens < 1:
            raise ValueError("num_tokens must be >= 1")

        self._storage.replenish(key, self._rate, self._capacity)
        return self._storage.consume(key, num_tokens)


def access_rate_handler(limiter: Limiter, key: str, is_async: bool = True):

    def decorator(func):
        async def wrapper(*args, **kwargs):
            while not limiter.consume(key):
                await asyncio.sleep(0.05)
            return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            while not limiter.consume(key):
                sleep(0.05)
            return func(*args, **kwargs)

        return wrapper if is_async else sync_wrapper

    return decorator


token_bank = MemoryStorage()
limiter_1 = Limiter(0.9, 1, token_bank)
limiter_10 = Limiter(9, 10, token_bank)
limiter_20 = Limiter(19, 20, token_bank)
quote_limiter = Limiter(1.2, 10, token_bank)
