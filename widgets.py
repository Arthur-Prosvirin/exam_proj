from PyQt6.QtWidgets import QLabel, QListWidget, QComboBox, QSpinBox, QPushButton


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


