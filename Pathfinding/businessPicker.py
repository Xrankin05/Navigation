from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class BusinessPicker(QWidget):
	def __init__(self, parent):
		super().__init__()  # Missing! This is very important
		self.parent = parent  # Reference to the main application

		# Dropdown Boxes
		self.pathfind_from = QComboBox()
		self.pathfind_from.setEditable(False)
		self.pathfind_to = QComboBox()
		self.pathfind_to.setEditable(False)

		# Search Button
		self.pathfind_button = QPushButton("Pathfind")
		self.pathfind_button.clicked.connect(self.pathfind)

		# Layout Setup
		self.layout = QVBoxLayout(self)
		self.layout.addWidget(QLabel("Start Business:"))
		self.layout.addWidget(self.pathfind_from)
		self.layout.addWidget(QLabel("End Business:"))
		self.layout.addWidget(self.pathfind_to)
		self.layout.addWidget(self.pathfind_button)

		self.update_list()  # Update list after setting up widgets

	def update_list(self):
		"""Updates the dropdown list with business names."""
		self.pathfind_to.clear()
		self.pathfind_from.clear()
		if self.parent.businesses:
			business_names = [business[0] for business in self.parent.businesses]  # Only names
			self.pathfind_from.addItems(business_names)
			self.pathfind_to.addItems(business_names)

	def pathfind(self):
		business_start_name = self.pathfind_from.currentText().strip()
		business_end_name = self.pathfind_to.currentText().strip()

		# Use parent's business_dict (safer and faster)
		start_coords = self.parent.business_dict[business_start_name]
		end_coords = self.parent.business_dict[business_end_name]

		# Set start and goal in the grid
		self.parent.start = self.parent.grid[start_coords[1]][start_coords[0]]  # [row][col] = [y][x]
		self.parent.goals = [self.parent.grid[end_coords[1]][end_coords[0]]]

		# Now run pathfinding
		self.parent.find_path()
