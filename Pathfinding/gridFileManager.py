from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import csv

class GridFileManager:
    def __init__(self, parent, folder_path):
        self.parent = parent  # Reference to the main application
        self.folder_path = folder_path  # Folder to scan for CSV files
        
        # Dropdown/Typing Box
        self.file_selector = QComboBox()
        self.file_selector.setEditable(True)  # Allows typing custom file names
        self.update_file_list()

        # Export Button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_grid)

        # Import Button
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_color) # TEMPORARILY CHANGING THIS OFF OF IMPORT_GRID TO TEST IMPORT_COLOR

        # Layout Setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.file_selector)
        self.layout.addWidget(self.export_button)
        self.layout.addWidget(self.import_button)
        #parent.main_layout.addLayout(self.layout)

    def update_file_list(self):
        """Updates the dropdown list with CSV files from the folder."""
        self.file_selector.clear()
        if os.path.exists(self.folder_path):
            csv_files = [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]
            self.file_selector.addItems(csv_files)

    def export_grid(self):
        """Saves the current grid state as a CSV file."""
        file_name = self.file_selector.currentText().strip()
        if not file_name.endswith('.csv'):
            file_name += '.csv'
        file_path = os.path.join(self.folder_path, file_name)
        
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in self.parent.grid:
                writer.writerow([f'{node.type}:{node.cost}:{node.accessible}' for node in row]) # EDIT THESE FOR EXPORTING/IMPORTING
        print(f"Grid exported to {file_path}")
        self.update_file_list()

    def import_grid(self):
        """Loads a grid state from a selected CSV file."""
        file_name = self.file_selector.currentText().strip()
        file_path = os.path.join(self.folder_path, file_name)
        
        if not os.path.exists(file_path):
            print("File not found!")
            return
        
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row_idx, row in enumerate(reader):
                for col_idx, values in enumerate(row):
                    node = values.split(":") # EDIT THESE BELOW TO ASSIGN NODE WITH VALUES FROM CSV
                    self.parent.grid[row_idx][col_idx].type = node[0]
                    self.parent.grid[row_idx][col_idx].color = self.parent.color_map[node[0]]
                    self.parent.grid[row_idx][col_idx].cost = node[1]
                    self.parent.grid[row_idx][col_idx].accessible = node[2]
                    #self.parent.grid[row_idx][col_idx].updateColor() # UPDATE COLOR BREAKS IT, BUT NEED TO FIGURE OUT HOW TO UPDATE PARENTS START AND GOAL NODES SOMEWHERE
        self.parent.real_color()
        print(f"Grid imported from {file_path}")


    def import_color(self):
            """Loads a grid state from a selected CSV file."""
            file_name = self.file_selector.currentText().strip()
            file_path = os.path.join(self.folder_path, file_name)
            print(os.getcwd())
            print (file_path)
            if not os.path.exists(file_path):
                print("File not found!")
                return
            
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                for row_idx, row in enumerate(reader):
                    for col_idx, value in enumerate(row):
                        value = eval(value)
                        color = QColor(value[0], value[1], value[2]) # R int G int B int values
                        self.parent.grid[row_idx][col_idx].type = 'reset'
                        self.parent.grid[row_idx][col_idx].color = color
                        self.parent.grid[row_idx][col_idx].cost = 1
                        self.parent.grid[row_idx][col_idx].accessible = 1
            self.parent.fake_color()
            print(f"Grid imported from {file_path}")