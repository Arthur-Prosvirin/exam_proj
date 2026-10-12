from abc import ABC, abstractmethod
from functools import total_ordering


class Entity(ABC):
    @abstractmethod
    def describe(self):
        pass


@total_ordering
class Event(Entity):
    def __init__(self, name, first, second, odd_first, odd_second):
        self.name, self.first, self.second = name, first, second
        self.odd_first, self.odd_second = odd_first, odd_second

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value).strip()

    @property
    def first(self):
        return self._first

    @first.setter
    def first(self, value):
        self._first = str(value)

    @property
    def second(self):
        return self._second

    @second.setter
    def second(self, value):
        self._second = str(value)

    @property
    def odd_first(self):
        return self._odd_first

    @odd_first.setter
    def odd_first(self, value):
        self._odd_first = max(1.01, float(value))

    @property
    def odd_second(self):
        return self._odd_second

    @odd_second.setter
    def odd_second(self, value):
        self._odd_second = max(1.01, float(value))

    def describe(self):
        return f"{self.name}: {self.first} — {self.second}"

    def __str__(self):
        return self.describe()

    def __repr__(self):
        return f"Event({self.name!r}, {self.first!r}, {self.second!r})"

    def __eq__(self, other):
        return isinstance(other, Event) and self.name == other.name

    def __lt__(self, other):
        if not isinstance(other, Event):
            return NotImplemented
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


@total_ordering
class Bet(Entity):
    def __init__(self, event, choice, amount, odd):
        self.event, self.choice, self.amount, self.odd = event, choice, amount, odd
        self.won = False

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if value <= 0:
            raise ValueError("Ставка должна быть положительной")
        self._amount = int(value)

    @property
    def odd(self):
        return self._odd

    @odd.setter
    def odd(self, value):
        self._odd = float(value)

    @property
    def won(self):
        return self._won

    @won.setter
    def won(self, value):
        self._won = bool(value)

    @property
    def choice(self):
        return self._choice

    @choice.setter
    def choice(self, value):
        self._choice = str(value)

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, value):
        self._event = value

    def describe(self):
        return f"{self.event.name}: {self.choice}, {self.amount} монет — {'Победа' if self.won else 'Проигрыш'}"

    def __str__(self):
        return self.describe()

    def __repr__(self):
        return f"Bet({self.choice!r}, {self.amount}, {self.odd})"

    def __eq__(self, other):
        return isinstance(other, Bet) and (self.amount, self.choice) == (other.amount, other.choice)

    def __lt__(self, other):
        if not isinstance(other, Bet):
            return NotImplemented
        return self.amount < other.amount

    def __hash__(self):
        return hash((self.amount, self.choice))


class Registry(Entity):
    """Свой аналог словаря без использования dict."""
    def __init__(self):
        self._keys, self._values = [], []

    def put(self, key, value):
        if key in self._keys:
            self._values[self._keys.index(key)] = value
        else:
            self._keys.append(key)
            self._values.append(value)

    def get(self, key, default=None):
        return self._values[self._keys.index(key)] if key in self._keys else default

    def describe(self):
        return f"Записей: {len(self._keys)}"

    def __len__(self):
        return len(self._keys)

    def __str__(self):
        return self.describe()

    def __repr__(self):
        return f"Registry({self._keys!r})"

    def __eq__(self, other):
        return isinstance(other, Registry) and self._keys == other._keys


