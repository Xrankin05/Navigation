from PyQt5.QtWidgets import QGraphicsRectItem  # Import for grid cell representation
from PyQt5.QtCore import Qt  # Import for event handling
from PyQt5.QtGui import *

class Node(QGraphicsRectItem):
    def __init__(self, row, col, width, total_rows, total_cols, parent, cost):
        super().__init__(0, 0, width, width)  # Initialize a square grid cell
        
        # Grid position and parent reference
        self.parent = parent  # Reference to the main application
        self.row = row  # Row index
        self.col = col  # Column index
        self.total_rows = total_rows  # Total number of rows in the grid
        self.total_cols = total_cols  # Total number of cols in the grid
        self.heuristic_to_goal = float("inf")
        self.f_score = float("inf")
        self.traversable = ["reset", "goal", "reset1", "reset2", "reset3"]
        self.streetName = ""

        self.setAcceptHoverEvents(True)  # Enable hover events
        self.setAcceptedMouseButtons(Qt.LeftButton)  # Accept left clicks
        
        # Set graphical properties
        self.setRect(col * width, row * width, width, width)  # Define cell position and size
        self.color = self.parent.color_map['reset']  # Default color
        self.setBrush(self.color)  # Set initial color fill

        # Pathfinding properties
        self.neighbors = []  # List to store accessible neighboring nodes
        self.width = width  # Width of each cell
        self.type = 'reset'  # Default type
        
        # Allow selection for user interaction
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)  # Enable hover events
        
        self.cost = cost  # Cost to move into this node
        self.accessible = True  # Whether the node is traversable (outdated)

    # For when nodes cost the same
    def __lt__(self, other):
        if self.f_score == other.f_score:
            # Prefer nodes closer to the goal
            return self.heuristic_to_goal < other.heuristic_to_goal  
        return False  # Otherwise, priority queue will use f_score by default

    # Resets the node to its default state (empty space)
    def reset(self):
        self.color = self.parent.color_map['reset']
        self.type = 'reset'
        self.setBrush(self.color)  # Update display color

    # Updates the list of accessible (non-barrier) neighbors. Checks up, down, left, and right.
    def update_neighbors(self, grid):
        self.neighbors = []
        
        # Check DOWN (row + 1) if it's within bounds and not a barrier
        if self.row < self.total_rows - 1 and grid[self.row + 1][self.col].type in self.traversable:
            self.neighbors.append(grid[self.row + 1][self.col])
        
        # Check UP (row - 1) if it's within bounds and not a barrier
        if self.row > 0 and grid[self.row - 1][self.col].type in self.traversable:
            self.neighbors.append(grid[self.row - 1][self.col])
        
        # Check RIGHT (col + 1) if it's within bounds and not a barrier
        if self.col < self.total_cols - 1 and grid[self.row][self.col + 1].type in self.traversable:
            self.neighbors.append(grid[self.row][self.col + 1])
        
        # Check LEFT (col - 1) if it's within bounds and not a barrier
        if self.col > 0 and grid[self.row][self.col - 1].type in self.traversable:
            self.neighbors.append(grid[self.row][self.col - 1])


    def updateColor(self):
        currType = self.type  # Store current type
        
        # Ensure start node is unique; do not allow multiple starts
        if self.parent.start and self.parent.selected_color == self.parent.color_map['start']:
            return  # Ignore click if a start node is already set
        
        # If the clicked node is the current start, remove it
        elif currType == 'start':
            self.parent.start = None
        
        # If the clicked node is a goal, remove it from the goal list
        elif currType == 'goal':
            try:
                self.parent.goals.remove(self)
            except:
                pass
        
        # Assign new node type based on the selected color
        if self.parent.selected_name:
            self.streetName = self.parent.selected_name
        if self.parent.selected_cost:
            self.cost = float(self.parent.selected_cost)
        if self.parent.selected_color == self.parent.color_map['start']:
            self.parent.start = self  # Set new start node
            self.currColor = self.parent.selected_color
            self.type = 'start'
            self.color = self.currColor
        
        elif self.parent.selected_color == self.parent.color_map['goal']:
            self.parent.goals.append(self)  # Add to goal list
            self.currColor = self.parent.selected_color
            self.type = 'goal'
            self.color = self.currColor
        
        elif self.parent.selected_color == self.parent.color_map['barrier']:
            self.currColor = self.parent.selected_color
            self.type = 'barrier'  # Mark as an obstacle
            self.color = self.currColor
        
        elif self.parent.selected_color == self.parent.color_map['reset3']:
            self.currColor = self.parent.selected_color
            self.type = 'reset3'  # Mark as empty
            self.color = self.currColor

        elif self.parent.selected_color == self.parent.color_map['reset2']:
            self.currColor = self.parent.selected_color
            self.type = 'reset2'  # Mark as empty
            self.color = self.currColor
        
        elif self.parent.selected_color == self.parent.color_map['reset']:
            self.currColor = self.parent.selected_color
            self.type = 'reset'  # Mark as empty
            self.color = self.currColor
        
        elif self.parent.selected_color == self.parent.color_map['path_point']:
            self.currColor = self.parent.selected_color
            self.type = 'path_point'  # Mark as path_point
            self.color = self.currColor

        elif self.parent.selected_color == self.parent.color_map['closed']:
            self.currColor = self.parent.selected_color
            self.type = 'closed'  # Mark as closed
            self.color = self.currColor
        
        # Apply the selected color to the node
        self.setBrush(self.parent.selected_color)

    # Start panning with right mouse button
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.parent.isLeftClicking = True
            self.updateColor()

    # End panning with right mouse button
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.parent.isLeftClicking = False

    #  Triggers when the mouse moves while the left button is held down
    def mouseMoveEvent(self, event):
        if self.parent.isLeftClicking:  # Ensure left click is held
            scene_pos = event.scenePos()  # Get position in scene coordinates
            items_under_cursor = self.scene().items(scene_pos)  # Get items at cursor

            for item in items_under_cursor:
                if isinstance(item, Node):  # Ensure it's a Node
                    item.updateColor()
                    break  # Avoid multiple updates

            event.accept()  # Accept event to stop further processing
        else:
            event.ignore()  # Ignore if the condition isn't met

        super().mouseMoveEvent(event)

    # Updates node info in info panel
    def hoverEnterEvent(self, event):
        self.parent.update_info_panel(self)
        super().hoverEnterEvent(event)

    # Clears node info in info panel
    def hoverLeaveEvent(self, event):
        self.parent.clear_info_panel()
        super().hoverLeaveEvent(event)

