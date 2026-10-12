import random
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from models import Event, Bet, Registry
from widgets import (TitleLabel, BalanceLabel, EventsList, OutcomeBox, AmountBox,
                     BetButton, AgainButton, OddsLabel, ResultLabel, HistoryList)

TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
REPORT = Path(__file__).with_name("report.txt")


class BetsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мини-ставки")
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


