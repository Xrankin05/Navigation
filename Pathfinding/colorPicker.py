from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QGridLayout, QSizePolicy, QTextEdit)
from PyQt5.QtCore import Qt

class ColorPicker(QWidget):

    def __init__(self, colors, parent):
        super().__init__()
        self.colors = colors
        self.parent = parent

        # Set a grid layout instead of vertical
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # Create labels and buttons
        row = 0
        col = 0
        for color_name, color_value in self.colors.items():
            label = QLabel(color_name)
            label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(label, row, col)

            button = QPushButton()
            button.setStyleSheet(f"background-color: {color_value.name()}; border: 1px solid black;")
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.clicked.connect(lambda _, c=color_value: self.set_selected_color(c))
            self.layout.addWidget(button, row + 1, col)

            col += 1
            if col >= 2:
                col = 0
                row += 2  # Move 2 rows down (label + button)
        row += 2
        col = 0
        label = QLabel("Street Name")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, row, col)
        self.textbox = QTextEdit()
        self.textbox.textChanged.connect(self.set_selected_name)
        self.layout.addWidget(self.textbox, row, col + 1)
        row += 2
        col = 0
        label = QLabel("Node Cost")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, row, col)
        self.costbox = QTextEdit()
        self.costbox.textChanged.connect(self.set_selected_cost)
        self.layout.addWidget(self.costbox, row, col + 1)

    def set_selected_color(self, color):
        self.parent.selected_color = color

    def set_selected_name(self):
        text = self.textbox.toPlainText()
        self.parent.selected_name = text

    def set_selected_cost(self):
        text = self.costbox.toPlainText()
        self.parent.selected_cost = text