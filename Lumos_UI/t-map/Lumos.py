from Lumos_View import CallHandler
from Lumos_View import Form
import find_way as FW


import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDir
from PyQt5.QtCore import QJsonValue
from PyQt5.QtCore import QJsonDocument
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QLabel


class Lumos(CallHandler, Form):
    def __init__(self):
        self.ch = CallHandler()
        self.form = Form()
        self.form.init_widget


    @pyqtSlot(str, name='setText')
    def set_text(self, v):
        print(v)

    @pyqtSlot(QJsonValue, name='webToAppSendData')
    def web_to_app_send_data(self, value):
        # QJasonValue 데이터를 Python Dict 형태로 변환
        data = CallHandler.recursive_qjsonvalue_convert(value)
        print(data)


    @pyqtSlot(QJsonValue, name='findWay')
    def findWay(self, value):
        global txt
        global button
        # QJasonValue 데이터를 Python Dict 형태로 변환
        data = CallHandler.recursive_qjsonvalue_convert(value)
        fw = FW.FindWay(data)
        txt = fw.get_ps();








txt = '';
if __name__ == "__main__":
    sys.argv.append("--remote-debugging-port=8000")
    app = QApplication(sys.argv)
    lumos=Lumos()
    exit(app.exec_())



