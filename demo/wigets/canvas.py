import imgviz
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, QPoint, Qt, QPointF
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QMenu

import demo.ai
import demo.utils

CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor

MOVE_SPEED = 5.0

class Canvas(QWidget):
    zoomRequest = Signal(int, QPoint)
    scrollRequest = Signal(int, int)
    selectionChanged = Signal(list)
    mouseMoved = Signal(QPointF)

    CREATE, EDIT = 0, 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = self.EDIT
        self.current = None
        self.offsets = QPoint(), QPoint()
        self.scale = 1.0
        self.pixmap = QPixmap()
        self.visible = {}
        self._hideBackround = False
        self.hideBackround = False
        self._painter = QPainter()
        self._cursor = CURSOR_DEFAULT
        self.menus = QMenu()
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)
        self._ai_model = None

    def drawing(self):
        return self.mode == self.CREATE

    def mouseMoveEvent(self, ev):
        try:
            pos = self.transformPos(ev.position().toPoint())
        except AttributeError:
            return

        self.mouseMoved.emit(pos)
        self.prevMovePoint = pos
        self.restoreCursor()

        is_shift_pressed = ev.modifiers() & Qt.ShiftModifier

    def paintEvent(self, event):
        if not self.pixmap:
            return super().paintEvent(event)

        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offsetToCenter())

        p.drawPixmap(0, 0, self.pixmap)
        p.end()

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.RightButton:
            menu = self.menus
            self.restoreCursor()
            if not menu.exec(self.mapToGlobal(ev.position().toPoint())):
                self.repaint()

    def setHiding(self, enable=True):
        self._hideBackround = self.hideBackround if enable else False

    def transformPos(self, point):
        point_f = QPointF(point)
        scale = self.scale
        offset = self.offsetToCenter()
        # 将QPointF转换为浮点数进行运算
        transformed_x = (point_f.x() / scale) - offset.x()
        transformed_y = (point_f.y() / scale) - offset.y()
        # 将结果转换回QPointF
        return QPointF(transformed_x, transformed_y)
    def offsetToCenter(self):
        s = self.scale
        area = self.size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def outOfPixmap(self, p):
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w - 1 and 0 <= p.y() <= h - 1)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super().minimumSizeHint()

    def wheelEvent(self, ev):
        mods = ev.modifiers()
        delta = ev.angleDelta()
        if not mods & Qt.ControlModifier:
            self.zoomRequest.emit(delta.y(), ev.position().toPoint())
        else:
            self.scrollRequest.emit(delta.x(), Qt.Horizontal)
            self.scrollRequest.emit(delta.y(), Qt.Vertical)
        ev.accept()
    def loadPixmap(self, pixmap):
        self.pixmap = pixmap
        if self._ai_model:
            self._ai_model.set_image(
                image=demo.utils.img_qt_to_arr(self.pixmap.toImage())
            )
        self.update()

    def overrideCursor(self, cursor):
        self.restoreCursor()
        self._cursor = cursor
        QtWidgets.QApplication.setOverrideCursor(cursor)

    def restoreCursor(self):
        QtWidgets.QApplication.restoreOverrideCursor()

    def resetState(self):
        self.restoreCursor()
        self.pixmap = None
        self.update()