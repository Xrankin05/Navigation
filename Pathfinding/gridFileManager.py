from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import csv

class GridFileManager:

    def __init__(self, parent, folder_path):
        self.parent = parent
        self.folder_path = folder_path  # Folder to scan for CSV files
        self.flipped = self.flip_dict(parent.color_map)
        # Dropdown/Typing Box
        self.file_selector = QComboBox()
        self.file_selector.setEditable(True)  # Allows typing custom file names
        self.update_file_list()

        # Export Button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_grid)

        # Import Grid Button
        self.import_grid_button = QPushButton("Import from Grid")
        self.import_grid_button.clicked.connect(self.import_grid)

        # Import From Exported Color JPG Button
        self.import_color_button = QPushButton("Import from Color")
        self.import_color_button.clicked.connect(self.import_color)

        # Layout Setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.file_selector)
        self.layout.addWidget(self.export_button)
        self.layout.addWidget(self.import_grid_button)
        self.layout.addWidget(self.import_color_button)

    # Updates the dropdown list with CSV files from the folder.
    def update_file_list(self):
        self.file_selector.clear()
        if os.path.exists(self.folder_path):
            csv_files = [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]
            self.file_selector.addItems(csv_files)

    # Exports current grid as filename
    def export_grid(self):
        file_name = self.file_selector.currentText().strip()
        if not file_name.endswith('.csv'):
            file_name += '.csv'
        file_path = os.path.join(self.folder_path, file_name)

        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            businesses_data = []
            for name, x, y, score in self.parent.businesses:
                businesses_data.extend([name, str(x), str(y), str(score)])  # one entry per field, extend instead of append to add all 3 seperately

            writer.writerow(businesses_data)

            for row in self.parent.grid:
                row_data = []
                for node in row:
                    r, g, b, _ = node.color.getRgb()
                    node_data = f"{node.type}:{r},{g},{b}:{node.cost}:{node.streetName}"
                    row_data.append(node_data)
                writer.writerow(row_data)
        print(f"Grid exported to {file_path}")
        self.update_file_list()

    # Import a grid state from a csv file
    def import_grid(self):
        file_name = self.file_selector.currentText().strip()
        file_path = os.path.join(self.folder_path, file_name)

        if not os.path.exists(file_path):
            print("File not found!")
            return

        with open(file_path, 'r') as file:
            lines = list(csv.reader(file))
            businesses_line = lines[0]
            self.parent.businesses = []

            i = 0
            while i < len(businesses_line):
                try:
                    name = businesses_line[i].strip()
                    x = int(businesses_line[i + 1].strip())
                    y = int(businesses_line[i + 2].strip())
                    score = float(businesses_line[i + 3].strip())
                    self.parent.businesses.append((name, x, y, score))
                except Exception as e:
                    print(f"Error parsing business at index {i}: {e}")
                i += 4  # Move to the next set
            
            print("Total businesses:", len(self.parent.businesses))
            self.parent.business_dict = { name: (int(x), int(y), float(score)) for name, x, y, score in self.parent.businesses }
            self.parent.business_picker.update_list()
            lines = lines[1:]
            row_count = len(lines)
            col_count = len(lines[0]) if lines else 0

            self.parent.createNewGrid(row_count, col_count)

            for row_idx, row in enumerate(lines):
                for col_idx, cell in enumerate(row):
                    try:
                        parts = cell.split(":")
                        node_type = parts[0]
                        r, g, b = map(int, parts[1].split(","))
                        cost = float(parts[2])
                        street_name = parts[3] if len(parts) > 3 else ""

                        node = self.parent.grid[row_idx][col_idx]
                        node.type = node_type
                        node.color = QColor(r, g, b)
                        node.setBrush(node.color)
                        node.cost = cost
                        node.streetName = street_name

                        # Maintain goal/start references
                        if node_type == 'start':
                            self.parent.start = node
                        elif node_type == 'goal':
                            self.parent.goals.append(node)

                    except Exception as e:
                        print(f"Error parsing cell [{row_idx},{col_idx}]: {e}")

        self.parent.fake_color()
        print(f"Grid imported from {file_path}")

    # Legacy code for import grid from color files for map image quick setup
    def import_color(self):
        file_name = self.file_selector.currentText().strip()
        file_path = os.path.join(self.folder_path, file_name)
        print(os.getcwd())
        print (file_path)
        if not os.path.exists(file_path):
            print("File not found!")
            return
        
        with open(file_path, 'r') as file:
            lines = list(csv.reader(file))
            row_count = len(lines)
            col_count = len(lines[0]) if lines else 0
            self.parent.createNewGrid(row_count, col_count)
            for row_idx, row in enumerate(lines):
                for col_idx, value in enumerate(row):
                    value = eval(value)
                    color = QColor(value[0], value[1], value[2]) # R int G int B int values
                    type = self.flipped[(color.red(), color.green(), color.blue())]
                    if type in ["reset", 'reset1', 'reset2', 'reset3']:
                        type = 'reset'
                    else:
                        type = 'barrier'
                    self.parent.grid[row_idx][col_idx].type = type
                    self.parent.grid[row_idx][col_idx].color = color
                    self.parent.grid[row_idx][col_idx].cost = 1
                    self.parent.grid[row_idx][col_idx].accessible = 1
                    self.parent.grid[row_idx][col_idx].streetName = "Test Street"
        self.parent.fake_color() # change this to real color to see traversable vs barrier
        print(f"Grid imported from {file_path}")

    # Used to flip the dictionary
    def flip_dict(self, d):
        return { (v.red(), v.green(), v.blue()): k for k, v in d.items() }