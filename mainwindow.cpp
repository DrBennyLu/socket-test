#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "myudp.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->lineEdit->setFocusPolicy(Qt::StrongFocus);
    ui->textBrowser->setFocusPolicy(Qt::NoFocus);
//#ifndef ROLE
//    ui->label->setText("Server");
//#else
//    ui->label->setText("Client");
//#endif
    tableFormat.setBorder(0);

    connect(ui->pushButton,SIGNAL(clicked()),this,SLOT(sendMessage()));
    //connect(ui->pushButton,SIGNAL(returnPressed()),this,SLOT(appendMessage(QString,QString)));
    connect(ui->lineEdit,SIGNAL(returnPressed()),this,SLOT(sendMessage()));
    connect(&myudp,SIGNAL(newMessage(QString,QString)),this,SLOT(appendMessage(QString,QString)));
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::appendMessage(const QString &from, const QString &message)
{
    if (from.isEmpty() || message.isEmpty())
        return;

    QTextCursor cursor(ui->textBrowser->textCursor());
    cursor.movePosition(QTextCursor::End);

    QTextTable *table = cursor.insertTable(1, 2, tableFormat);
    table->cellAt(0, 0).firstCursorPosition().insertText('<' + from + "> ");
    table->cellAt(0, 1).firstCursorPosition().insertText(message);
    QScrollBar *bar = ui->textBrowser->verticalScrollBar();
    bar->setValue(bar->maximum());
}

void MainWindow::sendMessage()
{
    QString text = ui->lineEdit->text();
    if (text.isEmpty())
        return;

    if (text.startsWith(QChar('/'))) {
        QColor color = ui->textBrowser->textColor();
        ui->textBrowser->setTextColor(Qt::red);
        ui->textBrowser->append(tr("! Unknown command: %1")
                                .arg(text.left(text.indexOf(' '))));
        ui->textBrowser->setTextColor(color);
    } else {
        //client.sendMessage(text);
        myudp.sendMessage(text);
#ifndef ROLE
        appendMessage("server", text);
#else
        appendMessage("client", text);
#endif
    }

    ui->lineEdit->clear();
}
