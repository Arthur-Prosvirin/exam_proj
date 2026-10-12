"""Учебные ставки на виртуальные монеты. PyQt6, без реальных денег."""
import random
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from functools import total_ordering
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
    QListWidget, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout, QGroupBox)

TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
REPORT = Path(__file__).with_name("report.txt")


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


class TitleLabel(QLabel):
    def __init__(self):
        super().__init__("МИНИ-СТАВКИ")
        self.setStyleSheet("font-size: 23px; font-weight: bold")


class BalanceLabel(QLabel):
    def __init__(self):
        super().__init__("Баланс: 1000 монет")
        self.setStyleSheet("font-size: 17px")


class EventsList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(280)


class OutcomeBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(180)


class AmountBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setRange(1, 100000)
        self.setValue(100)
        self.setSuffix(" монет")


class BetButton(QPushButton):
    def __init__(self):
        super().__init__("Сделать ставку")


class AgainButton(QPushButton):
    def __init__(self):
        super().__init__("Начать заново")


class OddsLabel(QLabel):
    def __init__(self):
        super().__init__("Коэффициент: —")


class ResultLabel(QLabel):
    def __init__(self):
        super().__init__("Выбери событие и сделай ставку")
        self.setWordWrap(True)


class HistoryList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(140)


class BetsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мини-ставки (виртуальная игра)")
        self.resize(680, 520)
        self.started = datetime.now()
        self.balance = 1000
        self.bets = []
        self.events = [
            Event("Матч 1", "Коты", "Собаки", 1.8, 2.1),
            Event("Матч 2", "Лисы", "Волки", 1.6, 2.4),
            Event("Матч 3", "Орлы", "Совы", 2.0, 1.9),
            Event("Матч 4", "Роботы", "Люди", 1.5, 2.6),
            Event("Матч 5", "Пираты", "Ниндзя", 2.2, 1.7),
            Event("Матч 6", "Драконы", "Рыцари", 1.4, 3.0),
            Event("Матч 7", "Марс", "Венера", 1.9, 1.9),
            Event("Матч 8", "Чай", "Кофе", 2.3, 1.6),
            Event("Матч 9", "Лето", "Зима", 1.7, 2.2),
            Event("Матч 10", "Кирпич", "Смартфон", 1.1, 10.0),
        ]
        self.stats = Registry()
        self.stats.put("Сыграно", 0)
        self.stats.put("Побед", 0)
        self.build()

    def build(self):
        self.title = TitleLabel()
        self.balance_label = BalanceLabel()
        self.events_list = EventsList()
        self.outcome = OutcomeBox()
        self.amount = AmountBox()
        self.bet_button = BetButton()
        self.again_button = AgainButton()
        self.odds = OddsLabel()
        self.result = ResultLabel()
        self.history = HistoryList()
        for event in self.events:
            self.events_list.addItem(str(event))
        self.events_list.setCurrentRow(0)
        self.events_list.currentRowChanged.connect(self.update_outcomes)
        self.outcome.currentIndexChanged.connect(self.update_odds)
        self.bet_button.clicked.connect(self.place_bet)
        self.again_button.clicked.connect(self.reset)
        left = QVBoxLayout()
        left.addWidget(QLabel("События:"))
        left.addWidget(self.events_list)
        right = QVBoxLayout()
        for widget in (QLabel("Исход:"), self.outcome, QLabel("Сумма:"),
                       self.amount, self.odds, self.bet_button, self.result,
                       self.again_button):
            right.addWidget(widget)
        right.addStretch()
        row = QHBoxLayout()
        row.addLayout(left, 2)
        row.addLayout(right, 1)
        root = QVBoxLayout(self)
        root.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.balance_label, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addLayout(row)
        root.addWidget(QLabel("История ставок:"))
        root.addWidget(self.history)
        self.update_outcomes()

    def update_outcomes(self):
        index = self.events_list.currentRow()
        if index < 0:
            return
        event = self.events[index]
        self.outcome.blockSignals(True)
        self.outcome.clear()
        self.outcome.addItems([event.first, event.second])
        self.outcome.blockSignals(False)
        self.update_odds()

    def update_odds(self):
        index = self.events_list.currentRow()
        if index < 0:
            return
        event = self.events[index]
        odd = event.odd_first if self.outcome.currentIndex() == 0 else event.odd_second
        self.odds.setText(f"Коэффициент: {odd:.2f}")

    def place_bet(self):
        if self.events_list.currentRow() < 0:
            return
        amount = self.amount.value()
        if amount > self.balance:
            self.result.setText("Недостаточно монет")
            return
        event = self.events[self.events_list.currentRow()]
        choice_index = self.outcome.currentIndex()
        choice = event.first if choice_index == 0 else event.second
        odd = event.odd_first if choice_index == 0 else event.odd_second
        bet = Bet(event, choice, amount, odd)
        self.balance -= amount
        # Результат имитируется случайным образом; реальные матчи не используются.
        bet.won = random.random() < 1 / odd
        if bet.won:
            self.balance += round(amount * odd)
        self.bets.append(bet)
        self.stats.put("Сыграно", len(self.bets))
        self.stats.put("Побед", self.stats.get("Побед") + int(bet.won))
        self.result.setText(f"{'Выигрыш!' if bet.won else 'Проигрыш.'} "
                            f"{'Получено ' + str(round(amount * odd)) if bet.won else 'Потеряно ' + str(amount)} монет")
        self.history.insertItem(0, str(bet))
        self.balance_label.setText(f"Баланс: {self.balance} монет")

    def reset(self):
        self.balance = 1000
        self.bets.clear()
        self.history.clear()
        self.stats.put("Сыграно", 0)
        self.stats.put("Побед", 0)
        self.result.setText("Баланс восстановлен")
        self.balance_label.setText("Баланс: 1000 монет")

    def closeEvent(self, event):
        ended = datetime.now()
        headings = ["login", "time_in", "time_out"]
        values = ["Guest", self.started.strftime(TIME_FORMAT), ended.strftime(TIME_FORMAT)]
        widths = [max(len(a), len(b)) for a, b in zip(headings, values)]
        border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
        line = lambda cells: "| " + " | ".join(str(c).ljust(w) for c, w in zip(cells, widths)) + " |"
        try:
            REPORT.write_text("\n".join([border, line(headings), border,
                                          line(values), border]) + "\n", encoding="utf-8")
        except OSError as exc:
            self.result.setText(f"Ошибка записи отчёта: {exc}")
            event.ignore()
            return
        event.accept()


app = QApplication(sys.argv)
window = BetsApp()
window.show()
sys.exit(app.exec())
