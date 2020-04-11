# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread

import psutil
import socket

# import os
import time
from pathlib import Path
import json

from tcpserver import TCPServer
from tcpclient import TCPClient

QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class MyApp(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        super(QtWidgets.QMainWindow, self).__init__()

        self.reconnect = False

        """Load UI"""
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.init_ui()

        self.ui.comboBox_Interface.currentIndexChanged.connect(
            self.on_interface_selection_change)
        self.ui.button_Refresh.clicked.connect(self.on_refresh_button_clicked)

        self.ui.button_TcpServer.clicked.connect(
            self.on_tcp_server_start_stop_button_clicked)
        self.ui.button_TcpServerSend.clicked.connect(
            self.on_tcp_server_message_send
        )

        self.ui.button_TcpClient.clicked.connect(
            self.on_tcp_client_connect_button_clicked
        )

    def init_ui(self):
        # Interface
        self.update_network_interfaces()

        # TCP Client
        self.ui.textBrowser_TcpClientMessage.setEnabled(False)
        self.ui.lineEdit_TcpClientSend.setEnabled(False)
        self.ui.button_TcpClientSend.setEnabled(False)

        self.ui.lineEdit_TcpClientTargetIP.setText('192.168.1.132')
        self.ui.lineEdit_TcpClientTargetPort.setText('1234')

        # TCP Server
        self.ui.textBrowser_TcpServerMessage.setEnabled(False)
        self.ui.lineEdit_TcpServerSend.setEnabled(False)
        self.ui.button_TcpServerSend.setEnabled(False)

        self.ui.lineEdit_TcpServerListenPort.setText('1234')

    def update_network_interfaces(self):
        self.ui.comboBox_Interface.clear()
        self.net_if = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        net_names = list(self.net_if.keys())

        for if_name in net_names:
            if not net_if_stats[if_name].isup:
                self.net_if.pop(if_name, None)
            else:
                self.ui.comboBox_Interface.addItem(if_name)

        self.ui.comboBox_Interface.setCurrentIndex(0)
        current_interface = self.ui.comboBox_Interface.currentText()

        for snicaddr in self.net_if[current_interface]:
            if snicaddr.family == socket.AF_INET:
                ipv4_add = snicaddr.address
                break
            else:
                ipv4_add = '0.0.0.0'

        self.ui.label_LocalIP.setText(ipv4_add)

    def on_interface_selection_change(self):
        current_interface = self.ui.comboBox_Interface.currentText()

        if current_interface in self.net_if:
            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    ipv4_add = snicaddr.address
                    break
                else:
                    ipv4_add = '0.0.0.0'
        else:
            return

        self.ui.label_LocalIP.setText(ipv4_add)

    def on_refresh_button_clicked(self):
        self.update_network_interfaces()

    # TCP Server
    def on_tcp_server_start_stop_button_clicked(self):
        if self.ui.button_TcpServer.text() == 'Start':
            self.ui.button_TcpServer.setEnabled(False)
            self.ui.lineEdit_TcpServerListenPort.setEnabled(False)
            self.tcp_server_thread = QThread()
            self.tcp_server = TCPServer(
                self.ui.label_LocalIP.text(),
                int(self.ui.lineEdit_TcpServerListenPort.text()))

            self.tcp_server_thread.started.connect(self.tcp_server.start)
            self.tcp_server.status.connect(self.on_tcp_server_status_update)
            self.tcp_server.message.connect(self.on_tcp_server_message_ready)

            self.tcp_server.moveToThread(self.tcp_server_thread)

            self.tcp_server_thread.start()

        elif self.ui.button_TcpServer.text() == 'Stop':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.close()

        elif self.ui.button_TcpServer.text() == 'Disconnect':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.disconnect()
            self.reconnect = True

    def on_tcp_server_status_update(self, status, addr):
        if status == TCPServer.ERROR:
            self.tcp_server.status.disconnect()
            self.tcp_server.message.disconnect()

            self.ui.button_TcpServer.setText('Start')
            self.tcp_server_thread.terminate()

            self.ui.textBrowser_TcpServerMessage.setEnabled(False)
            self.ui.lineEdit_TcpServerSend.setEnabled(False)
            self.ui.button_TcpServerSend.setEnabled(False)
            self.ui.lineEdit_TcpServerListenPort.setEnabled(True)

            if self.reconnect:
                self.reconnect = False
                self.on_tcp_server_start_stop_button_clicked()
        elif status == TCPServer.LISTEN:
            self.ui.button_TcpServer.setText('Stop')

            self.ui.textBrowser_TcpServerMessage.setEnabled(False)
            self.ui.lineEdit_TcpServerSend.setEnabled(False)
            self.ui.button_TcpServerSend.setEnabled(False)

        elif status == TCPServer.CONNECTED:
            self.ui.button_TcpServer.setText('Disconnect')

            self.ui.textBrowser_TcpServerMessage.setEnabled(True)
            self.ui.lineEdit_TcpServerSend.setEnabled(True)
            self.ui.button_TcpServerSend.setEnabled(True)
            # self.tcp_server.send('Hello World')

        self.ui.button_TcpServer.setEnabled(True)

    def on_tcp_server_message_ready(self, source, msg):
        self.ui.textBrowser_TcpServerMessage.append(msg)

    def on_tcp_server_message_send(self):
        self.tcp_server.send(self.ui.lineEdit_TcpServerSend.text())
        self.ui.lineEdit_TcpServerSend.clear()

    # TCP Client
    def on_tcp_client_connect_button_clicked(self):
        if self.ui.button_TcpClient.text() == 'Connect':
            self.ui.button_TcpClient.setEnabled(False)
            self.tcp_client_thread = QThread()
            self.tcp_client = TCPClient(self.ui.label_LocalIP.text(), 505)

            self.tcp_client_thread.started.connect(self.tcp_client.start)
            self.tcp_client.status.connect(self.on_tcp_client_status_update)

            self.tcp_client.moveToThread(self.tcp_client_thread)

            self.tcp_client_thread.start()

    def on_tcp_client_status_update(self, status, addr):
        print('tcp client status')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
