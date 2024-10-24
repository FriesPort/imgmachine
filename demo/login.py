from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys
from PySide6.QtWidgets import *
from utils import dbconnection

from config import *
from app import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()

        config=get_config()
        self.config=config

        self.resize(350, 450)
        self.znzz_statusLabel = QLabel()
        self.znzz_statusLabel.setStyleSheet("QLabel { color : red; font-size: 14px; }")

        self.znzz_user_combo = QComboBox()
        self.znzz_user_combo.setEditable(True)
        self.znzz_user_combo.setPlaceholderText("请输入账号")
        self.znzz_user_combo.lineEdit().setReadOnly(False)
        self.znzz_user_combo.lineEdit().setPlaceholderText("请输入账号")
        self.znzz_user_combo.setFixedSize(305, 50)
        self.znzz_user_combo.setStyleSheet("QComboBox { height: 50px; width: 300px; }")
        for item in self.config["login"]["username"]:
            self.znzz_user_combo.addItem(item)

        self.znzz_password_edi = QLineEdit()
        self.znzz_password_edi.setPlaceholderText("请输入密码")
        self.znzz_password_edi.setFixedSize(300, 50)
        self.znzz_password_edi.setStyleSheet("QLineEdit { height: 50px; width: 300px; }")
        self.znzz_password_edi.setEchoMode(QtWidgets.QLineEdit.Password)
        self.znzz_loginBtn = QPushButton("登录")
        self.znzz_loginBtn.setStyleSheet(
            "QPushButton{ "
            "background-color: rgb(0, 160, 255); "
            "color: white; "
            "height: 50px; "
            "width: 280px; "
            "font-size: 16px; "
            "font-family: 'Arial';"
            "text-align: center;"
            "padding: 10px; "
            "}"
        )

        self.znzz_loginBtn.clicked.connect(self.znzz_onLogin)

        # 创建布局并添加控件
        loginLayout = QVBoxLayout()

        loginLayout.addWidget(self.znzz_user_combo)
        loginLayout.addWidget(self.znzz_password_edi)
        loginLayout.addWidget(self.znzz_loginBtn)
        loginLayout.addWidget(self.znzz_statusLabel)

        loginLayout.setAlignment(self.znzz_user_combo, QtCore.Qt.AlignCenter)  # 设置用户名输入框居中
        loginLayout.setContentsMargins(30,10,30,10)
        loginLayout.setAlignment(self.znzz_password_edi, QtCore.Qt.AlignCenter)  # 设置密码输入框居中
        loginLayout.setAlignment(self.znzz_loginBtn, QtCore.Qt.AlignCenter)  # 设置登录按钮居中

        # 创建中央窗口并设置布局
        centralWidget = QWidget()
        centralWidget.setLayout(loginLayout)
        self.setCentralWidget(centralWidget)
    def znzz_onLogin(self):
        if(self.znzz_legal()):
            self.close()
            self.main_window = MainWindow()
            self.main_window.show()
        else:
            self.znzz_statusLabel.setText("登录失败：用户名或密码错误")

    #登录
    def znzz_legal(self):
        znzz_username=self.znzz_user_combo.currentText()
        znzz_password=self.znzz_password_edi.text()
        db=dbconnection.znzz_SQLiteConnection()
        znzz_login=db.znzz_dblogin(znzz_username,znzz_password)
        if znzz_login:
            self.znzz_store_user(znzz_username)
        return znzz_login

    def znzz_store_user(self, username):
        with open("default_config.yaml", 'r') as file:
            data = yaml.safe_load(file)
        if data == None:
            return False
        print(data)
        data['login']['user'] = [username]

        # 写入YAML文件
        with open("default_config.yaml", "w") as file:
            yaml.dump(data, file, default_flow_style=False)