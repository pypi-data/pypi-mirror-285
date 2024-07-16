# mypy: disable-error-code="var-annotated"
from __future__ import annotations

import weakref

from functools import reduce
from itertools import islice
from typing import Any, Hashable, Iterable, Mapping, Optional, Sequence


class Descriptor:
    """Base class for descriptors."""
    __dict__ = weakref.WeakKeyDictionary()

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        # Well behaved descriptors return themselves if the instance is `None`.
        if instance is None:
            return self
        elif self.name in instance.__dict__:
            return instance.__dict__[self.name]
        else:
            raise AttributeError(self.name)


class DataDescriptor(Descriptor):
    """Base class for data descriptors."""
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        if self.name in instance.__dict__:
            del instance.__dict__[self.name]
        else:
            raise AttributeError(self.name)


class ReadOnlyAttribute(DataDescriptor):
    """Descriptor for setting immutable attributes."""

    def __set__(self, instance, value):
        if self.name in instance.__dict__:
            raise AttributeError(f"attribute '{self.name}' is read-only")

        super().__set__(instance, value)

    def __delete__(self, instance):
        if self.name in instance.__dict__:
            raise AttributeError(f"attribute '{self.name}' is read-only")
        else:
            raise AttributeError(self.name)


def unique_sort(iterable: Iterable) -> tuple:
    """
    Remove duplicate values and perform a hierarchical sort on the iterable,
    sorting first by length, then by value.
    """
    return tuple(sorted(set(iterable), key=lambda x: (-len(x), x)))


def index_view(view, key: int) -> Any:
    """
    Index a dictionary view or view-like object at the spefified index
    position (key). The view must implement `__len__`.
    """
    if key < 0:
        key = len(view) - abs(key)

    return next(islice(view, key, key + 1))


def is_number(value: str) -> bool:
    """
    Indicates whether the value can be represented as a floating point number.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_homogeneous(iterable: Sequence[Any]) -> bool:
    """Indicates whether all of the values are identical."""
    return all(x == iterable[0] for x in iterable)


class Keymap(dict):

    def add(self, key: tuple[Hashable]) -> None:
        for subkey in key:
            self[subkey] = key

    def remove(self, key: tuple[Hashable]) -> None:
        for subkey in key:
            del self[subkey]


class Polymap(dict):
    """Mapping which allows multiple keys to be mapped to the same values."""

    def __init__(self, mapping: Optional[Mapping] = None, /, **kwargs):
        self._keymap = Keymap()
        self.update(mapping, **kwargs)

    @classmethod
    def fromkeys(cls, iterable, value = None) -> Polymap:
        mapping = cls()
        mapping.update({k: value for k in iterable})
        return mapping

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if key in self:
                # Update the master key.
                super().__setitem__(key, value)
            else:
                for subkey in key:
                    if subkey in self._keymap:
                        raise KeyError(f"'{subkey}' is already bound")

                    if subkey in self:
                        # Allow ownership of the ubound key to be transferred
                        # to the master key.
                        del self[subkey]

                super().__setitem__(key, value)
                self._keymap.add(key)
        else:
            super().__setitem__(self._keymap.get(key, key), value)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return super().__getitem__(item)
        return super().__getitem__(self._keymap.get(item, item))

    def __delitem__(self, key):
        if isinstance(key, tuple):          # It's a master key.
            self._keymap.remove(key)
            super().__delitem__(key)
        elif key in self._keymap:           # It's a bound key.
            master = self._keymap.get(key, key)
            self._keymap.remove(master)
            super().__delitem__(master)
        else:
            super().__delitem__(key)        # It's an unbound key.

    def __contains__(self, item):
        if item in self._keymap.values():
            return True
        return item in self._keymap.keys()

    def keys(self) -> set:
        return self._keymap.values() | super().keys()

    def items(self) -> tuple:
        return ((k, self[k]) for k in self.keys())

    def update(self, mapping: Optional[Mapping] = None, /, **kwargs) -> None:
        if mapping:
            for k, v in mapping.items():
                self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def pop(self, key):
        # Must use subclass `__getitem__` and `__delitem__`.
        value = self[key]
        del self[key]
        return value

    def get(self, key, default: Any = None):
        if key in self:
            return self[key]
        return default

    def clear(self) -> None:
        super().clear()
        self._keymap.clear()

    def setdefault(self, key, default: Any = None):
        self[key] = default


class MappingView:
    """
    Mapping proxy for storing mappings which are not meant to be mutated
    directly. Allows for membership testing, iteration, and attribute access on
    the underlying mapping, but restricts attribute and item assignment.
    """
    __hash__ = None

    def __init__(self, mapping: dict | Mapping):
        self._mapping = mapping

    def keys(self):
        return self._mapping.keys()

    def values(self):
        return self._mapping.values()

    def items(self):
        return self._mapping.items()

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def __contains__(self, key):
        return key in self._mapping

    def __getitem__(self, key):
        return self._mapping[key]

    def __iter__(self):
        return self._mapping.__iter__()

    def __reversed__(self):
        return self._mapping.__reversed__()

    def __repr__(self):
        return self._mapping.__repr__()

    def __str__(self):
        return self.__repr__()


class SetFamily(set):
    """
    A set-of-sets, which allows membership testing for elements of
    subsets.

     We call a set which is a child of the parent a member of the family.
     Invidual values within a member are referred to as elements. A
     `SetFamily` should be viewed as one continuous set. When testing for
     membership, the user is expected to test for the existence of a specific
     element, rather than a member, or use a public method which
     specifically allows testing for members.
    """
    def __init__(self, members: Optional[set] = None):
        if members:
            super().__init__([self._coerce(m) for m in members])
        else:
            super().__init__()

    @property
    def superset(self):
        """Reduce the members to a single set."""
        return reduce(lambda x, y: x.union(y), self)

    @staticmethod
    def _coerce(iterable: Iterable):
        return frozenset(iterable)

    def includes(
            self,
            element: Hashable,
            superset: bool = False
            ) -> SetFamily | frozenset:
        """
        Return all of the members which contain the element. If `superset`
        is true, return the union of the containing members.
        """
        parents = SetFamily([v for v in self if element in v])
        if not superset or not parents:
            return parents
        return reduce(lambda x, y: x.union(y), parents)

    def __contains__(self, element: Hashable):
        for member in self:
            if element in member:
                return True
        else:
            return False

    def add(self, member) -> None:
        member = self._coerce(member)
        super().add(member)

    def update(self, *others: Iterable):
        # Iterate over the flattened iterable.
        for member in (member for family in others for member in family):
            self.add(member)

    def copy(self):
        return SetFamily(super().copy())
