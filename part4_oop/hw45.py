from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return self._data.get(key) is not None

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self.remove_key(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        return self._order[0] if len(self._order) > self.capacity else None

    def remove_key(self, key: K) -> None:
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def register_access(self, key: K) -> None:
        self._key_counter[key] = self._key_counter.get(key, 0) + 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) > self.capacity:
            sorted_keys_by_use_count = sorted(self._key_counter.items(), key=lambda x: x[1])
            last_added_key = list(self._key_counter.keys())[-1]

            if sorted_keys_by_use_count[0][0] != last_added_key:
                return sorted_keys_by_use_count[0][0]

            return sorted_keys_by_use_count[1][0]

        return None

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._key_counter)


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)

        to_delete = self.policy.get_key_to_evict()

        if to_delete is not None:
            self.storage.remove(to_delete)
            self.policy.remove_key(to_delete)

    def get(self, key: K) -> V | None:
        if self.storage.exists(key):
            self.policy.register_access(key)
            return self.storage.get(key)

        return None

    def exists(self, key: K) -> bool:
        exists = self.storage.exists(key)

        if exists:
            self.policy.register_access(key)

        return exists

    def remove(self, key: K) -> None:
        if self.storage.exists(key):
            self.policy.remove_key(key)
            self.storage.remove(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func

    def __get__(self, instance: HasCache[Any, V] | None, owner: type) -> "CachedProperty[V] | V | None":
        if instance is None:
            return self

        key = self._func.__name__

        if instance.cache.exists(key):
            return instance.cache.get(key)

        res = self._func(instance)
        instance.cache.set(key, res)

        return res
