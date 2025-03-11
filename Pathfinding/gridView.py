from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPainter


class GridView(QGraphicsView):
	def __init__(self, scene: QGraphicsScene):
		super().__init__(scene)
		self.setRenderHint(QPainter.Antialiasing, True)

		# Disable scrollbars entirely
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		# Enable smooth transformations
		self.setTransformationAnchor(QGraphicsView.NoAnchor)
		self.setResizeAnchor(QGraphicsView.NoAnchor)
		self.setDragMode(QGraphicsView.NoDrag)

		# Track panning state
		self.last_mouse_pos = None
		self.panning = False

	def wheelEvent(self, event: QWheelEvent):
		"""Zoom in and out smoothly at cursor location."""
		zoom_factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
		mouse_scene_pos = self.mapToScene(event.pos())

		# Apply zoom relative to cursor position
		self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.scale(zoom_factor, zoom_factor)
		self.setTransformationAnchor(QGraphicsView.NoAnchor)

	def mousePressEvent(self, event: QMouseEvent):
		"""Start panning when right-click is pressed."""
		if event.button() == Qt.RightButton:
			self.last_mouse_pos = event.pos()
			self.panning = True
			self.setCursor(Qt.ClosedHandCursor)

	def mouseMoveEvent(self, event: QMouseEvent):
		"""Move the scene instead of using scrollbars."""
		if self.panning and self.last_mouse_pos:
			# Convert screen delta to scene delta
			delta = self.mapToScene(event.pos()) - self.mapToScene(self.last_mouse_pos)
			self.translate(-delta.x(), -delta.y())  # Directly move scene view
			self.last_mouse_pos = event.pos()

	def mouseReleaseEvent(self, event: QMouseEvent):
		"""Stop panning when right mouse button is released."""
		if event.button() == Qt.RightButton:
			self.panning = False
			self.setCursor(Qt.ArrowCursor)
