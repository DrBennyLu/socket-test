from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import socket


class TCPServer(QObject):
    status = pyqtSignal(int, object)
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2

    def __init__(self, ip, port):
        QObject.__init__(self)

        self.ip = ip
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @pyqtSlot()
    def start(self):
        try:
            self.tcp_socket.bind((self.ip, self.port))
            self.tcp_socket.listen(1)

            while True:
                # Wait for a connection
                print('wait for a connection')
                self.status.emit(self.LISTEN, '')
                self.connection, client_address = self.tcp_socket.accept()

                self.status.emit(self.CONNECTED, client_address)

                try:
                    # Receive the data in small chunks and retransmit it
                    while True:
                        data = self.connection.recv(16)

                        if data:
                            self.connection.sendall(data)
                        else:
                            break
                finally:
                    # Clean up the connection
                    print('close connection')
                    if self.connection is not None:
                        self.connection.close()

        except OSError as err:
            # print(err)
            # raise
            print('emit error')
            self.status.emit(self.ERROR, '')

    def send(self, msg):
        self.connection.sendall(msg.encode())

    def disconnect(self):
        self.connection.close()
        self.connection = None
        print('close connection')

    def close(self):
        self.tcp_socket.close()
        print('close socket')
