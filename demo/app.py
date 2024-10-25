import datetime
import functools
import io
import math
import os
import re
import PIL.Image
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6 import  QtWidgets, QtGui, QtCore

from natsort import natsort

from config import *
from demo import __appname__
from demo import utils
from demo.wigets.zoom_widget import ZoomWidget
from demo.wigets.tool_Bar import ToolBar
from demo.wigets.canvas import Canvas
from demo.utils import dbconnection
from check import judge
from ultralytics import YOLO


class MainWindow(QMainWindow):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = 0, 1, 2
    def __init__(self, znzz_config=None, znzz_filename=None):
        if znzz_config is None:
            znzz_config = get_config()
        self._config = znzz_config
        if znzz_filename is not None and osp.isdir(znzz_filename):
            self.znzz_importDirImages(znzz_filename, load=False)
        else:
            self.znzz_filename = znzz_filename
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

        # 数据展示栏
        self.znzz_dataShow_List = QListWidget()
        #self.znzz_dataShow_List.itemSelectionChanged.connect()
        self.znzz_dataShow_List.setObjectName("数据展示")
        self.znzz_dataShow_List.setToolTip("数据展示")
        self.znzz_dataShow_dock = QDockWidget()
        self.znzz_dataShow_List = QListWidget()

        self.znzz_dataShow_dock.setObjectName("数据展示窗口")
        self.znzz_dataShow_dock.setWidget(self.znzz_dataShow_List)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.znzz_dataShow_dock)
        self.znzz_zoomWidget = ZoomWidget()
        # 创建 Canvas 实例
        self.znzz_canvas = Canvas()
        self.znzz_canvas.zoomRequest.connect(self.zoomRequest)
        # 创建 滑动框
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(self.znzz_canvas)
        scrollArea.setWidgetResizable(True)
        self.znzz_scrollBars = {
            Qt.Vertical: scrollArea.verticalScrollBar(),
            Qt.Horizontal: scrollArea.horizontalScrollBar(),
        }
        self.znzz_canvas.scrollRequest.connect(self.scrollRequese)
        # 将 QScrollArea 设置为中心部件
        self.setCentralWidget(scrollArea)
        # 侧边窗口-员工信息
        # self.znzz_employeeMes_list = QListWidget()
        # self.znzz_employeeMes_dock = QDockWidget(self)
        # self.znzz_employeeMes_dock.setObjectName("员工信息")
        # self.znzz_employeeMes_dock.setWidget(self.znzz_employeeMes_list)

        # 侧边窗口-文件
        self.znzz_file_dock = QDockWidget(self)
        self.znzz_file_dock.setObjectName("文件")

        self.znzz_fileSearch_lineEdit = QLineEdit()
        self.znzz_fileSearch_lineEdit.setPlaceholderText("搜索文件")
        self.znzz_fileSearch_lineEdit.textChanged.connect(self.fileSearch)

        self.znzz_fileList_list = QListWidget()
        self.znzz_fileList_list.itemSelectionChanged.connect(self.fileSelectionChanged)
        znzz_fileLayout = QVBoxLayout()
        znzz_fileLayout.setContentsMargins(0, 0, 0, 0)
        znzz_fileLayout.setSpacing(0)
        znzz_fileLayout.addWidget(self.znzz_fileSearch_lineEdit)
        znzz_fileLayout.addWidget(self.znzz_fileList_list)
        znzz_fileWid = QWidget()
        znzz_fileWid.setLayout(znzz_fileLayout)
        self.znzz_file_dock.setWidget(znzz_fileWid)

        # 窗口添加到右侧
        #self.addDockWidget(Qt.RightDockWidgetArea, self.znzz_employeeMes_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.znzz_file_dock)

        self.status("%s 启动成功" % __appname__)
        self.statusBar().show()

        self.resize(QSize(1500, 1000))

        znzz_action = functools.partial(utils.newAction, self)
        znzz_imgqualified = znzz_action(
            "合格",
            self.znzz_imgqualified,
            icon="done",
            enabled=False
        )
        znzz_imgunqualified = znzz_action(
            "不合格",
            self.znzz_imgunqualified,
            icon="cancel",
            enabled=False
        )
        znzz_prevImg = znzz_action(
            "上一张",
            self.znzz_prevImg,
            icon="prev",
            enabled=False
        )
        znzz_nextImg = znzz_action(
            "下一张",
            self.znzz_nextImg,
            icon="next",
            enabled=False
        )

        self.actions = utils.struct(
            znzz_nextImg=znzz_nextImg,
            znzz_prevImg=znzz_prevImg,
            znzz_imgunqualified=znzz_imgunqualified,
            znzz_imgqualified=znzz_imgqualified,
            znzz_menu=(
                znzz_imgqualified,
                znzz_imgunqualified,
                None,
                znzz_prevImg,
                znzz_nextImg
            ),
        )
        utils.addActions(
            self.znzz_canvas.menus,
            self.actions.znzz_menu
        )

        self.znzz_menus = utils.struct(
            file=self.znzz_menu("文件"),
        )
        znzz_open = znzz_action(
            "打开文件",
            self.openFile,
            icon="open"
        )
        znzz_opendir = znzz_action(
            "打开文件夹",
            self.opendir,
            icon="open"
        )
        utils.addActions(
            self.znzz_menus.file,
            (
                znzz_open,
                znzz_opendir
            )
        )
        # 参数初始化

        self.lastOpenDir = None
        self.opendDir = None
        self.image = QtGui.QImage()
        self.imagePath = None
        self.otherData = None
        self.zoom_level = 100
        self.zoom_values = {}
        self.zoomMode = self.FIT_WINDOW
        self.scroll_values = {
            Qt.Vertical: {},
            Qt.Horizontal: {},
        }

        if znzz_filename is not None and osp.isdir(znzz_filename):
            self.znzz_importDirImages(znzz_filename, load=False)
        else:
            self.znzz_filename = znzz_filename
        self.settings = QtCore.QSettings("demo", "demo")
        self.znzz_zoomWidget.setEnabled(False)
        self.znzz_zoomWidget.valueChanged.connect(self.paintCanvas)
        #self.queueEvent(functools.partial(self.loadFile, self.znzz_filename))

    # def queueEvent(self, func):
    #     QtCore.QTimer.singleShot(0, func)
    def status(self, message, delay=2000):
        self.statusBar().showMessage(message, delay)

    def znzz_importDirImages(self, dirPath, pattern=None, load=True):
        self.actions.znzz_nextImg.setEnabled(True)
        self.actions.znzz_prevImg.setEnabled(True)
        self.actions.znzz_imgqualified.setEnabled(True)
        self.actions.znzz_imgunqualified.setEnabled(True)

        self.lastOpenDir = dirPath
        self.znzz_filename = None
        self.znzz_fileList_list.clear()

        filesName = self.znzz_scanAllImages(dirPath)
        if pattern:
            try:
                filesName = [f for f in filesName if re.search(pattern, f)]
            except re.error:
                self.status(re.error)
        for znzz_filename in filesName:
            self.znzz_fileList_list.addItem(znzz_filename)
        self.znzz_nextImg()

    def znzz_scanAllImages(self, folderPath):
        extensions = [
            ".%s" % fmt.data().decode().lower()
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]
        images = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.normpath(osp.join(root, file))
                    images.append(relativePath)
        images = natsort.os_sorted(images)

        return images

    # 人工检测合格
    #TODO 需要有一个获取当前处理图片的绝对路劲的方法，由于我们处理的图片是标记过后的，不是原图片，考虑是否把标记过后的图片的绝对路径也存储到数据库中
    def znzz_imgqualified(self):
        self.znzz_nextImg()
        # 假设此处可以获取当前正在处理的图像的绝对路径
        current_image_path = self.get_current_image_path()
        db=dbconnection.znzz_SQLiteConnection()
        db.znzz_check(current_image_path,"OK")
        self.status("检测结果为正确，已存储")
    #不合格
    def znzz_imgunqualified(self):
        self.znzz_nextImg()
        # 假设此处可以获取当前正在处理的图像的绝对路径
        current_image_path = self.get_current_image_path()
        db=dbconnection.znzz_SQLiteConnection()
        db.znzz_check(current_image_path,"NG")
        self.status("检测结果为错误")

    def znzz_nextImg(self):
        self.znzz_selectImg(next=True)

    def znzz_prevImg(self):
        self.znzz_selectImg(prev=True)

    def znzz_selectImg(self, load=True, next=False, prev=False):
        lst = self.imageList()
        if len(lst) <= 0:
            return
        if self.znzz_filename is None:
            self.znzz_filename = lst[0]
        else:
            currentIndex = self.znzz_fileList_list.currentIndex()
            model = currentIndex.model() if currentIndex.isValid() else None
            if model is not None:
                currentIndexRow = currentIndex.row()
                totalRows = model.rowCount()
                if next and currentIndexRow + 1 < totalRows:
                    znzz_filename = lst[currentIndexRow + 1]
                elif prev and currentIndexRow - 1 >= 0:
                    znzz_filename = lst[currentIndexRow - 1]
                else:
                    return
                self.znzz_filename = znzz_filename
            else:
                self.errorMessage("提醒", "卡了")
                return
        if self.znzz_filename and load:
            self.loadFile(self.znzz_filename)
    def fileSelectionChanged(self):
        items = self.znzz_fileList_list.selectedItems()
        if not items:
            return
        item = items[0]

        lst = self.imageList()

        currIndex = lst.index(str(item.text()))
        if currIndex < len(lst):
            znzz_filename = lst[currIndex]
            if znzz_filename:
                self.loadFile(znzz_filename)

    def scrollRequese(self, delta, orientation):
        units = -delta * 0.1
        bar = self.znzz_scrollBars[orientation]
        value = bar.value() + bar.singleStep() * units
        self.setScroll(orientation, value)

    def setScroll(self, orientation, value):
        self.znzz_scrollBars[orientation].setValue(int(value))
        self.scroll_values[orientation][self.znzz_filename] = value

    def zoomRequest(self, delta, pos):
        canvas_width_old = self.znzz_canvas.width()
        units = 1.1
        if delta < 0:
            units = 0.9
        self.addZoom(units)

        canvas_width_new = self.znzz_canvas.width()
        if canvas_width_old != canvas_width_new:
            canvas_scale_factor = canvas_width_new / canvas_width_old

            x_shift = round(pos.x() * canvas_scale_factor) - pos.x()
            y_shift = round(pos.y() * canvas_scale_factor) - pos.y()

            self.setScroll(
                Qt.Horizontal,
                self.znzz_scrollBars[Qt.Horizontal].value() + x_shift,
            )
            self.setScroll(
                Qt.Vertical,
                self.znzz_scrollBars[Qt.Vertical].value() + y_shift,
            )

    def setZoom(self, value):
        self.zoomMode = self.MANUAL_ZOOM
        self.znzz_zoomWidget.setValue(value)
        self.zoom_values[self.znzz_filename] = (self.zoomMode, value)

    def addZoom(self, increment=1.1):
        zoom_value = self.znzz_zoomWidget.value() * increment
        if increment > 1:
            zoom_value = math.ceil(zoom_value)
        else:
            zoom_value = math.floor(zoom_value)
        self.setZoom(zoom_value)

    def resetState(self):
        self.znzz_filename = None

        self.imgPath = None
        self.imgData = None
        self.labelFile = None
        self.otherData = None
        self.znzz_canvas.resetState()

    def loadFile(self, znzz_filename=None):
        if znzz_filename in self.imageList() and (
                self.znzz_fileList_list.currentRow() != self.imageList().index(znzz_filename)
        ):
            self.znzz_fileList_list.setCurrentRow(self.imageList().index(znzz_filename))
            self.znzz_fileList_list.repaint()
            return
        self.resetState()
        self.znzz_canvas.setEnabled(False)

        if znzz_filename is None:
            znzz_filename = self.settings.value("znzz_filename", "")
        znzz_filename = str(znzz_filename)
        if not QtCore.QFile.exists(znzz_filename):
            self.errorMessage(
                "文件打开失败",
                "不存在该文件: <b>%s</b>" % znzz_filename,
            )
            return False

        # Load image
        self.status("加载 %s中..." % osp.basename(str(znzz_filename)))
        imageData = self.load_image_file(znzz_filename)
        if not imageData:
            self.errorMessage(
                "文件打开失败",
                "文件读取失败 <b>%s</b>" % znzz_filename,
            )
            self.status("读取错误 %s" % znzz_filename)
            return False

        image = QtGui.QImage.fromData(imageData)
        if image.isNull():
            formats = [
                "*.{}".format(fmt.data().decode())
                for fmt in QtGui.QImageReader.supportedImageFormats()
            ]
            self.errorMessage(
                "文件打开失败",
                (
                    "<p>请确保文件名合法.<br/>"
                    "支持文件格式为: {1}</p>"
                ).format(znzz_filename, ",".join(formats)),
            )
            self.status("读取错误 %s" % znzz_filename)
            return False

        self.image = image
        self.znzz_filename = znzz_filename
        self.znzz_canvas.loadPixmap(QtGui.QPixmap.fromImage(image))
        self.znzz_canvas.setEnabled(True)
        #设置缩放值
        if self.znzz_filename in self.zoom_values:
            self.zoomMode = self.zoom_values[self.znzz_filename][0]
            self.setZoom(self.zoom_values[self.znzz_filename][1])
        # set scroll values
        for orientation in self.scroll_values:
            if self.znzz_filename in self.scroll_values[orientation]:
                self.setScroll(
                    orientation, self.scroll_values[orientation][self.znzz_filename]
                )
        self.paintCanvas()
        self.znzz_canvas.setFocus()
        self.status("加载成功 %s" % osp.basename(str(znzz_filename)))
        return True

    def load_image_file(self, znzz_filename):
        try:
            image_pil = PIL.Image.open(znzz_filename)
        except IOError:
            self.errorMessage("error", "无法打开该文件夹: {}".format(znzz_filename))
            return

        # apply orientation to image according to exif
        image_pil = utils.apply_exif_orientation(image_pil)

        with io.BytesIO() as f:
            ext = osp.splitext(znzz_filename)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                format = "JPEG"
            else:
                format = "PNG"
            image_pil.save(f, format=format)
            f.seek(0)
            return f.read()

    def imageList(self):
        lst = []
        for i in range(self.znzz_fileList_list.count()):
            item = self.znzz_fileList_list.item(i)
            lst.append(item.text())
        return lst

    def paintCanvas(self):
        assert not self.image.isNull(), "无法显示该图像"
        self.znzz_canvas.scale = 0.01 * self.znzz_zoomWidget.value()
        self.znzz_canvas.adjustSize()
        self.znzz_canvas.update()

    def openFile(self, _value=False):
        # if not self.mayContinue():
        #     return
        path = osp.dirname(str(self.znzz_filename)) if self.znzz_filename else "."
        formats = [
            "*.{}".format(fmt.data().decode())
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]
        filters = self.tr("图像和标签文件 (%s)") % " ".join(
            formats + ["*%s" % ".json"]
        )
        fileDialog = QtWidgets.QFileDialog(self)
        fileDialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        fileDialog.setNameFilter(filters)
        fileDialog.setWindowTitle("%s - 选择文件" % __appname__)
        fileDialog.setWindowFilePath(path)
        fileDialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if fileDialog.exec_():
            znzz_filename = fileDialog.selectedFiles()[0]
            if znzz_filename:
                self.loadFile(znzz_filename)

    def opendir(self):
        if self.lastOpenDir and osp.exists(self.lastOpenDir):
            defaultOpenDir = self.lastOpenDir
        else:
            defaultOpenDir = osp.dirname(self.znzz_filename) if self.znzz_filename else "."
        targetDirPath = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "%s - 打开文件夹" % __appname__,
                defaultOpenDir,
                QtWidgets.QFileDialog.ShowDirsOnly
                | QtWidgets.QFileDialog.DontResolveSymlinks,
            )
        )
        self.opendDir = targetDirPath
        self.znzz_importDirImages(targetDirPath)

    def znzz_menu(self, title, actions=None):
        znzz_menu = self.menuBar().addMenu(title)
        if actions:
            utils.addActions(znzz_menu, actions)
        return znzz_menu

    def fileSearch(self):
        text = self.znzz_fileSearch_lineEdit.text()
        self.znzz_importDirImages(self.lastOpenDir, pattern=text, load=False)



    def errorMessage(self, title, message):
        return QtWidgets.QMessageBox.critical(
            self, title, "<p><b>%s</b></p>%s" % (title, message)
        )

    #获取绝对路径
    def znzz_getFilePath(self):
        self.znzz_canvas.update()
        znzz_filepath_list=self.znzz_scanAllImages(self)
        print(znzz_filepath_list)
        return znzz_filepath_list

    #按钮：检测
    #把获取的路径发送给算法模块，然后拿到检测结果
    #是否连同图片一起接收？
    '''
    我们获取图片路径是由qt视图所控制的，
    那么其他函数需要获取到的路径应该重新调函数还是访问控件中的信息？
    '''
    def AppController(self):
        self.znzz_createTable()
        znzz_fileList=self.znzz_getFilePath()
        znzz_checkResult=None
        path = "../check/83_0_15.jpg"
        img_path="./runs/detect/predict/"
        best="../check/best.pt"
        if znzz_fileList is not None:
            #TODO 调用算法模块，传入路径集合,给znzz_checkResult赋值
            path=self.opendDir
            judge.ngJudge(path,img_path,best)

        elif znzz_fileList is None:
            return '获取图片的绝对路径为NULL'



    #确定存储检测结果的表是否存在，如果没有就新建一个
    def znzz_createTable(self):
        with dbconnection.znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE TYPE='table'AND name='checklist'")
            table_exist=cursor.fetchone()
            if not table_exist:
                znzz_create_table_sql = """
                        CREATE TABLE checklist (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_count INTEGER,
                        machine_check_result TEXT,
                        manual_check_result TEXT,
                        absolute_path TEXT,
                        detected_part_type TEXT,
                        created_by TEXT,
                        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_by TEXT,
                        updated_time DATETIME DEFAULT CURRENT_TIMESTAMP
                     );
                """
                cursor.execute(znzz_create_table_sql)
                db.commit()
                cursor.close()


