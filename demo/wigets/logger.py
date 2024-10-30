from PySide6 import QtWidgets
from datetime import datetime

class Logger(QtWidgets.QDialog):
    """
    日志记录器类，用于显示日志信息。
    """

    def __init__(self, parent=None):
        super(Logger, self).__init__(parent)
        self.setWindowTitle("日志")  # 设置对话框标题

        self.table_widget = QtWidgets.QTableWidget(self)
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["检测人", "图片路径", "状态", "时间"])
        self.table_widget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)


        # 允许调整列宽
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        #self.table_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.table_widget)
        self.setLayout(self.layout)

    def add_log(self, ID, path, status):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        curTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items = [
            QtWidgets.QTableWidgetItem(ID),
            QtWidgets.QTableWidgetItem(path),
            QtWidgets.QTableWidgetItem(status),
            QtWidgets.QTableWidgetItem(curTime)
        ]

        for i, item in enumerate(items):
            self.table_widget.setItem(row_position, i, item)

        self.table_widget.scrollToBottom()