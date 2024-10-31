import imgviz
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, QPoint, Qt, QPointF
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QMenu

import demo.ai
import demo.utils

# 定义移动速度常量
MOVE_SPEED = 5.0

class Canvas(QWidget):
    # 定义信号，用于在缩放、滚动、选择变化和鼠标移动时发出
    zoomRequest = Signal(int, QPoint)
    scrollRequest = Signal(int, int)
    selectionChanged = Signal(list)
    mouseMoved = Signal(QPointF)

    # 定义模式常量：创建和编辑
    CREATE, EDIT = 0, 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化当前操作对象
        self.current = None
        # 初始化偏移量
        self.offsets = QPoint(), QPoint()
        # 初始化缩放比例
        self.scale = 1.0
        # 初始化图片
        self.pixmap = QPixmap()
        # 初始化可见性字典
        self.visible = {}
        # 初始化是否隐藏背景
        self._hideBackround = False
        self.hideBackround = False
        # 初始化画笔
        self._painter = QPainter()
        # 初始化右键菜单
        self.menus = QMenu()
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        # 设置焦点策略
        self.setFocusPolicy(Qt.WheelFocus)

    def mouseMoveEvent(self, ev):
        # 处理鼠标移动事件
        try:
            pos = self.transformPos(ev.position().toPoint())
        except AttributeError:
            return

        self.mouseMoved.emit(pos)
        self.prevMovePoint = pos
        self.restoreCursor()

    def paintEvent(self, event):
        # 处理绘画事件
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
        # 处理鼠标释放事件
        if ev.button() == Qt.RightButton:
            menu = self.menus
            self.restoreCursor()
            if not menu.exec(self.mapToGlobal(ev.position().toPoint())):
                self.repaint()

    def setHiding(self, enable=True):
        # 设置是否隐藏背景
        self._hideBackround = self.hideBackround if enable else False

    def transformPos(self, point):
        # 转换坐标位置
        point_f = QPointF(point)
        scale = self.scale
        offset = self.offsetToCenter()
        transformed_x = (point_f.x() / scale) - offset.x()
        transformed_y = (point_f.y() / scale) - offset.y()
        return QPointF(transformed_x, transformed_y)

    def offsetToCenter(self):
        # 计算偏移量以居中显示图片
        s = self.scale
        area = self.size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def outOfPixmap(self, p):
        # 检查点是否在图片外
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w - 1 and 0 <= p.y() <= h - 1)

    def sizeHint(self):
        # 返回建议的大小
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        # 返回最小大小
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super().minimumSizeHint()

    def wheelEvent(self, ev):
        # 处理滚轮事件
        mods = ev.modifiers()
        delta = ev.angleDelta()
        if not mods & Qt.ControlModifier:
            self.zoomRequest.emit(delta.y(), ev.position().toPoint())
        else:
            self.scrollRequest.emit(delta.x(), Qt.Horizontal)
            self.scrollRequest.emit(delta.y(), Qt.Vertical)
        ev.accept()

    def loadPixmap(self, pixmap):
        # 加载图片
        self.pixmap = pixmap
        self.update()

    def overrideCursor(self, cursor):
        # 覆盖当前光标
        self.restoreCursor()
        self._cursor = cursor
        QtWidgets.QApplication.setOverrideCursor(cursor)

    def restoreCursor(self):
        # 恢复默认光标
        QtWidgets.QApplication.restoreOverrideCursor()

    def resetState(self):
        # 重置状态
        self.restoreCursor()
        self.pixmap = None
        self.update()