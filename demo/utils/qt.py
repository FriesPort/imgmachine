import os.path as osp
from math import sqrt
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

here = osp.dirname(osp.abspath(__file__))
#为组件添加图标
def newIcon(icon):
    icons_dir = osp.join(here, "../icons")
    return QtGui.QIcon(osp.join(":/", icons_dir, f"{icon}.png"))
#创建一个新按钮
def newButton(text, icon=None, slot=None):
    b = QtWidgets.QPushButton(text)
    if icon is not None:
        b.setIcon(newIcon(icon))
    if slot is not None:
        QtCore.QObject.connect(b, QtCore.QEvent.MouseButtonRelease, slot)
    return b
#组件行为
def newAction(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, enabled=True, checked=False):
    a = QtGui.QAction(text, parent)  # QAction is now imported from QtGui
    if icon is not None:
        a.setIconText(text.replace(" ", "\n"))
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    a.setChecked(checked)
    return a
#为组件添加行为
def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QtWidgets.QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)

# 创建一个标签验证器函数，用于验证输入的字符串是否符合特定的正则表达式规则
def labelValidator():
    return QtGui.QRegExpValidator(QtCore.QRegExp(r"^[^ \t].+"), None)

class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

