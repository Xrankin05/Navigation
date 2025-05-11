from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from queue import PriorityQueue
from gridNode import Node
from colorPicker import ColorPicker
from businessPicker import BusinessPicker
from gridFileManager import GridFileManager
from gridView import GridView
from AIAPI import AIAPI

# Window and grid configuration
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
ROWS, COLS = 160, 320
GRID_WIDTH = int(WINDOW_WIDTH * 2 / 3)
GRID_HEIGHT = int(WINDOW_HEIGHT * 2 / 3)
CELL_SIZE = 10

# Color mapping for cell types
color_map = {
    "closed": QColor(171, 211, 223), # BLUE
    "reset2": QColor(233, 151, 163), # RED
    "reset3": QColor(245, 244, 198), # YELLOW
    "path_point": QColor(198, 193, 189), # GREY
    "goal": QColor(128, 0, 128), # PURPLE
    "reset": QColor(255, 183, 156), # ORANGE
    "start": QColor(255, 192, 203), # PINK
    "barrier": QColor(0, 0, 0), # BLACK
    "reset1": QColor(255, 255, 255), # WHITE
    "open": QColor(0, 255, 0) # GREEN
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Grid with Pathfinding")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.selected_color = color_map["barrier"]
        self.selected_name = ""
        self.selected_cost = ""
        self.color_map = color_map
        self.start = None
        self.goals = []
        self.businesses = []
        self.business_dict = { name: (x, y, score) for name, x, y, score in self.businesses }
        self.savedGridsPath = 'Pathfinding/Grids/'
        self.isLeftClicking = False
        self.stop_requested = False


        # For rectangle fill feature
        self.rectangle_fill_start = None
        self.rectangle_fill_active = False

        # Main widget and layout
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Horizontal split (Grid vs Controls)
        split_layout = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(split_layout)

        # Grid Area
        grid_area = QWidget()
        grid_layout = QVBoxLayout(grid_area)
        split_layout.addWidget(grid_area)

        # GridView and Scene
        self.scene = QGraphicsScene()
        self.view = GridView(self.scene)
        self.view.setMouseTracking(True)
        self.view.setFocusPolicy(Qt.StrongFocus)
        self.setFocusPolicy(Qt.StrongFocus)
        self.view.setFocus()
        self.view.setMinimumSize(600, 400)
        grid_layout.addWidget(self.view)

        # Info Label
        info_panel = QWidget()
        info_layout = QHBoxLayout(info_panel)

        self.info_label = QLabel("Hover over a cell to see info")
        self.info_label.setMinimumHeight(60)
        self.info_label.setStyleSheet("background-color: #f0f0f0; padding: 6px; font-family: monospace;")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label, 1)

        self.directions_box = QTextEdit()
        self.directions_box.setReadOnly(True)
        self.directions_box.setMinimumHeight(60)
        self.directions_box.setStyleSheet("background-color: #f9f9f9; padding: 6px; font-family: monospace;")
        info_layout.addWidget(self.directions_box, 2)

        grid_layout.addWidget(info_panel)

        # Create Grid
        self.grid = [[Node(row, col, CELL_SIZE, ROWS, COLS, self, 1) for col in range(COLS)] for row in range(ROWS)]
        for row in self.grid:
            for cell in row:
                self.scene.addItem(cell)

        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        split_layout.addWidget(right_panel)

        self.color_picker = ColorPicker(color_map, self)
        right_layout.addWidget(self.color_picker)

        self.gridFileManager = GridFileManager(self, self.savedGridsPath)
        layout_widget = QWidget()
        layout_widget.setLayout(self.gridFileManager.layout)
        right_layout.addWidget(layout_widget)

        self.business_picker = BusinessPicker(self)
        right_layout.addWidget(self.business_picker)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.find_path)
        right_layout.addWidget(self.run_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.request_stop)
        right_layout.addWidget(self.stop_button)
        
        ## Used for updating map based on color not given type
        #self.update_types_button = QPushButton("Update Types from Colors")
        #self.update_types_button.clicked.connect(self.update_types_from_colors)
        #right_layout.addWidget(self.update_types_button) 

        self.reset_visualizer_button = QPushButton("Reset Visualizer")
        self.reset_visualizer_button.clicked.connect(self.real_color)
        right_layout.addWidget(self.reset_visualizer_button)

        self.reset_board_button = QPushButton("Reset Board")
        self.reset_board_button.clicked.connect(self.reset_grid)
        right_layout.addWidget(self.reset_board_button)

    
    def find_path(self):
        print("Starting A* Pathfinding...")
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid)  # Updates all nodes in the grid with their neighbors.

        goals = self.goals[:]
        if not self.start or not goals:
            print("No start or goals set!")
            return

        current_start = self.start
        full_path = []  # List to store the full path across all goals
        
        for goal in goals:
            print(f"Finding path to goal at ({goal.row}, {goal.col})") 
            self.stop_requested = False  # Reset stop flag before starting


            # Initialize the priority queue for open set
            open_set = PriorityQueue()
            open_set.put((0, current_start))
            came_from = {}  # Dictionary to keep track of the path
            closed_set = set()  # Set to track fully checked nodes
            g_score = {node: float("inf") for row in self.grid for node in row}
            g_score[current_start] = 0
            f_score = {node: float("inf") for row in self.grid for node in row}
            f_score[current_start] = self.heuristic(current_start, goal)

            open_set_hash = {current_start}

            while not open_set.empty():
                if self.stop_requested:
                    print("[INFO] Pathfinding stopped by user.")
                    self.fake_color()
                    return

                _, current = open_set.get()
                open_set_hash.remove(current)

                if current in closed_set:
                    continue

                if current == goal:
                    print(f"Goal at ({goal.row}, {goal.col}) reached!")
                    segment_path = self.reconstruct_path(came_from, current)  # Get the segment path
                    full_path.extend(segment_path)  # Append to full path
                    current_start = goal  # Update the start for the next segment
                    break  # Exit loop and move to the next goal

                for neighbor in current.neighbors:
                    temp_g_score = g_score[current] + neighbor.cost / 80 # Edit this to tweak weights (100)

                    if temp_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = temp_g_score
                        heuristic = self.heuristic(neighbor, goal)
                        f_score[neighbor] = temp_g_score + heuristic
                        neighbor.heuristic_to_goal = heuristic
                        neighbor.f_score = f_score[neighbor]

                        if neighbor not in open_set_hash:
                            open_set.put((f_score[neighbor], neighbor))
                            open_set_hash.add(neighbor)
                            self.set_preview_color(neighbor, self.color_map['open'])
                            QApplication.processEvents()
                
                closed_set.add(current)
                self.set_preview_color(current, self.color_map['closed'])
                QApplication.processEvents()

            else:
                # If we exit the while loop without breaking, no path was found
                print(f"No path found to goal at ({goal.row}, {goal.col})!")
                self.real_color()
                return  # Stop searching if one goal is unreachable

        # After all goals are processed, reconstruct the entire path taken
        print("Reconstructing full path through all goals...") 
        self.visualize_full_path(full_path)
        print("All goals reached!") 
        print("Generating Play By Play") 
        self.generate_directions_from_path(full_path)



    def request_stop(self):
        print("[INFO] Pathfinding stop requested.")
        self.stop_requested = True


    # Manhattan distance
    def heuristic(self, node1, node2):
        dx = abs(node2.col - node1.col)
        dy = abs(node2.row - node1.row)
        return dx + dy


    # Reconstructs the path from goal to start and returns it
    def reconstruct_path(self, came_from, current):
        path_segment = []
        while current in came_from:
            current = came_from[current]
            if current != self.start:
                self.set_preview_color(current, self.color_map['path_point'])
                QApplication.processEvents()  # Force UI update
                path_segment.append(current)  # Store in path list
        
        path_segment.reverse()  # Reverse to get start -> goal order
        return path_segment

    # Given a list of nodes , return a list of dictionaries with row, col, and street name
    def get_path_summary(self, path_nodes):
        summary = []

        for node in path_nodes:
            entry = {
                "row": node.row,
                "col": node.col,
                "street": node.streetName.strip() if node.streetName else "Unnamed Road"
            }
            summary.append(entry)

        return summary

    # OpenAI call with path summary to get normal map navigational readings
    def generate_directions_from_path(self, path_nodes):
        if not path_nodes:
            self.directions_box.setText("No path found.")
            return

        # Prepare the path summary
        summary = self.get_path_summary(path_nodes)

        # Format it as a string
        path_text = "[\n" + ",\n".join([
            f"{{\"row\": {n['row']}, \"col\": {n['col']}, \"street\": \"{n['street']}\"}}"
            for n in summary
        ]) + "\n]"

        # Send the prompt to OpenAI
        try:
            ai = AIAPI()
            apiResponse = ai.getAPIResponse(path_text)

            if apiResponse is None:
                # Exceptions
                print('API Call Failed\n Exiting ...')
                apiResponse = f"Error with API Request, most likely insufficient api tokens.\n{path_text}"
            else:
                print(f'ChatGPT Response\n--------------------\n{apiResponse}\n--------------------')

            self.directions_box.setText(apiResponse)

        except Exception as e:
            self.directions_box.setText(f"Error generating directions: {e}")

    # Visually reconstructs the entire path across all goals
    def visualize_full_path(self, full_path):
        for node in full_path:
            self.set_preview_color(node, self.color_map['start'])
            QApplication.processEvents()

    def set_preview_color(self, cell, color):
        cell.color = color
        cell.setBrush(color)

    def real_color(self):
        for row in self.grid:
            for cell in row:
                cell.color = color_map[cell.type]
                cell.setBrush(cell.color)
    
    def fake_color(self):
        print("Fake Color Called")
        for row in self.grid:
            for cell in row:
                cell.setBrush(cell.color)

    def reset_grid(self):
        for row in self.grid:
            for cell in row:
                cell.reset()
        self.start = None
        self.goals = []
        print("Grid reset.")
    
    def createNewGrid(self, rows, cols):
        self.grid = [[Node(row, col, CELL_SIZE, rows, cols, self, 1) for col in range(cols)] for row in range(rows)]
        self.start = None
        self.goals = []
        self.scene.clear()
        for row in self.grid:
            for cell in row:
                self.scene.addItem(cell)

    # Rectangle Fill Stuff
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_T and not event.isAutoRepeat():
            self.rectangle_fill_active = True
            pos = self.view.mapFromGlobal(QCursor.pos())
            scene_pos = self.view.mapToScene(pos)
            items = self.scene.items(scene_pos)
            for item in items:
                if isinstance(item, Node):
                    self.rectangle_fill_start = (item.row, item.col)
                    print(f"[DEBUG] Rectangle fill start: {self.rectangle_fill_start}")
                    break

    # Rectangle Fill Stuff
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_T and not event.isAutoRepeat() and self.rectangle_fill_start:
            pos = self.view.mapFromGlobal(QCursor.pos())
            scene_pos = self.view.mapToScene(pos)
            items = self.scene.items(scene_pos)
            for item in items:
                if isinstance(item, Node):
                    start_row, start_col = self.rectangle_fill_start
                    end_row, end_col = item.row, item.col
                    print(f"[DEBUG] Rectangle fill end: ({end_row}, {end_col})")

                    top = min(start_row, end_row)
                    bottom = max(start_row, end_row)
                    left = min(start_col, end_col)
                    right = max(start_col, end_col)

                    for r in range(top, bottom + 1):
                        for c in range(left, right + 1):
                            node = self.grid[r][c]
                            node.updateColor()
                    break

            self.rectangle_fill_start = None
            self.rectangle_fill_active = False

    def update_info_panel(self, node):
        text = f"[Row: {node.row}, Col: {node.col}]\n"
        text += f"Type: {node.type}, Cost: {node.cost}, Accessible: {node.accessible}\n"
        text += f"Street Name: {node.streetName}"
        self.info_label.setText(text)

    def clear_info_panel(self):
        self.info_label.setText("Hover over a cell to see info")

    # Update all node types based on their current color
    def update_types_from_colors(self):
        updated = 0
        color_to_type = {v.name(): k for k, v in self.color_map.items()}

        for row in self.grid:
            for node in row:
                color_name = node.color.name()
                if color_name in color_to_type:
                    node_type = color_to_type[color_name]
                    node.type = node_type
                    updated += 1
                else:
                    print(f"[WARNING] Unknown color for node at ({node.row}, {node.col}): {color_name}")
        print(f"[INFO] Updated {updated} node types from color.")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
