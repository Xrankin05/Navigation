from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QSplitter, QFrame, QLabel, QGraphicsRectItem, QGraphicsScene, 
                             QGraphicsView, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from queue import PriorityQueue
from gridNode import Node

class ColorPicker(QWidget):
    """Widget to display color selection buttons on the right panel."""

    def __init__(self, colors, parent):
        """
        Initializes the color picker panel with buttons for each available color.

        Parameters:
        - colors: Dictionary mapping color names to QColor objects.
        - parent: Reference to the main application window for accessing shared attributes.
        """
        super().__init__()
        self.colors = colors  # Store color mapping
        self.parent = parent  # Reference to main application window
        self.layout = QVBoxLayout(self)  # Set layout for stacking elements vertically
        self.setLayout(self.layout)

        # Create buttons for each color
        for link in self.colors:
            # Create a label with the name of the color
            label = QLabel(link)
            label.setAlignment(Qt.AlignCenter)  # Center-align text
            self.layout.addWidget(label)

            # Create a button with the corresponding color as its background
            button = QPushButton()
            button.setStyleSheet(f"background-color: {self.colors[link].name()}; border: 1px solid black;")
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Make buttons expand
            button.clicked.connect(lambda _, c=se
