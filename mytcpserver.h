/*
//    mytcpserver.h
//
//    Copyright (C) 2017  Zach (Zhengyu) Peng, https://zpeng.me
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef MYTCPSERVER_H
#define MYTCPSERVER_H

#include <QTcpSocket>
#include <QTcpServer>

class MyTCPServer : public QTcpServer
{
    Q_OBJECT
public:
    explicit MyTCPServer(QObject *parent = nullptr);
    void listen(QHostAddress addr, quint16 port);

signals:
    void newMessage(const QString &from, const QString &message);

private slots:
    void clientConnection();
    void clientDisconnected();
    void messageReady();

private:
    QTcpSocket *tcpSocket;
    QTcpServer *tcpServer;
    QByteArray array;
};

#endif // MYTCPSERVER_H
