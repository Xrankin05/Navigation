from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from queue import PriorityQueue
from gridNode import Node
from colorPicker import ColorPicker   #comment i made by tanisha

# Constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
ROWS, COLS = 800, 100  # Grid size
GRID_WIDTH = int(WINDOW_WIDTH * 2 / 3)  # Left section (2/3 of the window)
GRID_HEIGHT = WINDOW_HEIGHT
CELL_SIZE = GRID_WIDTH // COLS  # Adjusting size per cell

# Colors
BLUE = QColor(0, 0, 255)
RED = QColor(255, 0, 0)
GREEN = QColor(0, 255, 0)
YELLOW = QColor(255, 255, 0)
PURPLE = QColor(128, 0, 128)
ORANGE = QColor(255, 165, 0)
PINK = QColor(255, 192, 203)
BLACK = QColor(0, 0, 0)
WHITE = QColor(255, 255, 255)

color_map = {
    "start": BLUE,
    "goal": PINK,
    "path_point": YELLOW,
    "barrier": BLACK,
    "reset": WHITE,
    "closed": RED,
    "open": GREEN
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Grid with Pathfinding")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.selected_color = BLACK  # Default color
        self.color_map = color_map
        self.start = None
        self.goals = []

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QSplitter(Qt.Horizontal)  # Splitter for left and right sections
        main_widget.setLayout(QVBoxLayout())
        main_widget.layout().addWidget(main_layout)
        self.setCentralWidget(main_widget)

        # === GRID SECTION (LEFT 2/3) ===
        self.scene = QGraphicsScene(0, 0, GRID_WIDTH, GRID_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(GRID_WIDTH, GRID_HEIGHT)

        # Create Grid
        self.grid = [[Node(row, col, CELL_SIZE, ROWS, COLS, self, 1) for col in range(COLS)] for row in range(ROWS)]
        for row in self.grid:
            for cell in row:
                self.scene.addItem(cell)

        # === COLOR PICKER & BUTTONS SECTION (RIGHT 1/3) ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Color Picker
        self.color_picker = ColorPicker(color_map, self)
        right_layout.addWidget(self.color_picker)

        # Add Replay Time Label and Text Box
        self.replay_time_label = QLabel("Replay Time (ms):")
        self.replay_time_input = QLineEdit()
        self.replay_time_input.setReadOnly(True)  # Make the text box read-only
        right_layout.addWidget(self.replay_time_label)
        right_layout.addWidget(self.replay_time_input)

        # Run Button
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.find_path)
        right_layout.addWidget(self.run_button)

        # Reset Visualizer Button
        self.reset_button = QPushButton("Reset Visualizer")
        self.reset_button.clicked.connect(self.real_color)
        right_layout.addWidget(self.reset_button)

        # Reset Board Button
        self.reset_button = QPushButton("Reset Board")
        self.reset_button.clicked.connect(self.reset_grid)
        right_layout.addWidget(self.reset_button)

        # Add sections to main layout
        main_layout.addWidget(self.view)  # Grid (left)
        main_layout.addWidget(right_panel)  # Right panel (color picker + buttons)

    
    def find_path(self):
        print("Starting A* Pathfinding...")  # Debugging
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid) # Updates all nodes in the grid with their neighbors.

        goals = self.goals[:]
        if not self.start or not goals:
            print("No start or goal set!")  # Debugging
            return
        
        goal = goals[0]
        # Initialize the priority queue for open set
        open_set = PriorityQueue()
        open_set.put((0, self.start))
        came_from = {} # Dictionary to keep track of the path
        g_score = {node: float("inf") for row in self.grid for node in row}
        g_score[self.start] = 0
        f_score = {node: float("inf") for row in self.grid for node in row}
        f_score[self.start] = self.heuristic(self.start, goal)

        open_set_hash = {self.start}
        
        while not open_set.empty():
            _, current = open_set.get()
            open_set_hash.remove(current)
            print(f"Checking node: ({current.row}, {current.col})")  # Debugging

            if current == goal:
                print("Goal reached!")  # Debugging
                self.reconstruct_path(came_from, current)
                return

            for neighbor in current.neighbors:
                temp_g_score = g_score[current] + neighbor.cost

                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + self.heuristic(neighbor, goal)
                    
                    if neighbor not in open_set_hash:
                        open_set.put((f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
                        self.set_preview_color(neighbor, self.color_map['open'])
                        print(f"Neighbor ({neighbor.row}, {neighbor.col}) added to open set.")  # Debugging
                        QApplication.processEvents()
            
            self.set_preview_color(current, self.color_map['closed'])
            QApplication.processEvents()

        print("No path found!")  # Debugging
        self.real_color()


    def heuristic(self, node1, node2):
        """Heuristic function for A* (Manhattan distance)"""
        return abs(node1.row - node2.row) + abs(node1.col - node2.col)

    def reconstruct_path(self, came_from, current):
        """Reconstructs the path from goal to start"""
        while current in came_from:
            current = came_from[current]
            if current != self.start:
                self.set_preview_color(current, self.color_map['path_point'])
                QApplication.processEvents()  # <-- Forces UI update

        #self.real_color()



    def set_preview_color(self, cell, color):
        cell.color = color
        cell.setBrush(color)

    def real_color(self):
        for row in self.grid:
            for cell in row:
                cell.color = color_map[cell.type]
                cell.setBrush(cell.color)

    def reset_grid(self):
        """Resets the grid to its initial state."""
        for row in self.grid:
            for cell in row:
                cell.reset()
        self.start = None
        self.goals = []
        print("Grid reset.")  # Debugging output

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
