import sys, os
import subprocess
import pandas as pd
from qtpy_cfg import *
from datetime import datetime
from pymongo import MongoClient
from PyQt5.QtCore import (
    Qt,
    QDate,
    QRect,
    QTimer,
    QObject,
    QThread,
    QDateTime,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QPen,
    QFont,
    QColor,
    QBrush,
    QPainter,
    QTextCharFormat,
)
from PyQt5.QtWidgets import (
    QLabel,
    QFrame,
    QWidget,
    QTextEdit,
    QLineEdit,
    QComboBox,
    QListWidget,
    QPushButton,
    QDockWidget,
    QMainWindow,
    QApplication,
    QTableWidget,
    QCalendarWidget,
    QTableWidgetItem,
)

sys.path.insert(1, "C:\\Users\\mount\\source\\repos\\MyDashboard\\MODULES\\")
from ubEnigma import write_txt_file, read_txt_file


mongo = db("mydb", "appointments")
now = datetime.now()


class Appointments(MongoClient):
    """
    This class pulls the data from MongoDb to populate
    the appointments table
    """
    def appointments(self):
        appts = []
        now = datetime.now()
        today = now.strftime("%m-%d-%Y")

        data = mongo.find(
            {}, {"_id": 0, "date": 1, "time": 1, "place": 1, "note": 1}
        ).sort("date")
        for d in data:
            if d["date"] < today:
                pass
            else:
                date, time, place, note = (
                    d["date"][:5],
                    d["time"],
                    d["place"],
                    d["note"],
                )
                appts.append([date, time, place, note])
        return appts


class Calendar(QCalendarWidget):
    """
    Initiates the calendar widget
    """
    def __init__(self, parent=None):
        super(Calendar, self).__init__()


class Example(QMainWindow):
    """
    GUI that houses the calendar and appointment list.
    A popup window (dock widget) is used to add appointments.
    """
    def __init__(self, parent=None):
        super(Example, self).__init__(parent)
        self.left   = 1138
        self.top    = 30
        self.width  = 302
        self.height = 445
        self.items = QDockWidget("dock", self)
        self.appointments = Appointments()
        self.cal = QCalendarWidget(self)
        format = QTextCharFormat()

        qblack(self)
        qdim = qbutton_calc(self)
        canda_10 = QFont("Candalara", 10)
        canda_11 = QFont("Candalara", 11)
        canda_12 = QFont("Candalara", 12)
        segoe_9  = QFont("Segoe UI", 9)
        segoe_16 = QFont("Segoe UI", 16)
        qgreen   = qbutton_green(self)
        style1   = "background-color: black"
        format   = self.cal.weekdayTextFormat(Qt.Saturday)
        format.setForeground(QBrush(Qt.darkCyan, Qt.SolidPattern))

        # Frame1 contains the widgets for adding an appointment.
        # This becomes the central widget required by dock widget.
        self.frame1 = QFrame(self)
        self.frame1.setStyleSheet(style1)
        self.items.setWidget(self.frame1) # Sets frame1 as the dock widget

        qtbutton(
            self.frame1, "save", 15, 350, 270, 30, qdim, canda_10, "SAVE", self.repeat
        )
        qtbutton(
            self.frame1, "exit", 15, 390, 270, 30, qdim, canda_10, "EXIT", self.close
        )

        # Builds the "date" label that shows the chosen appointment date
        self.date_data = QLabel(self.frame1)
        self.date_data.setGeometry(0, 35, 301, 40)
        self.date_data.setStyleSheet(
            "QLabel {color: rgba(125,125,125,255); background-color: black;}"
        )
        self.date_data.setFont(segoe_16)
        self.date_data.setAlignment(Qt.AlignCenter)

        # Builds the "time" label that shows the chosen appointment time
        self.time_label = QLabel(self.frame1)
        self.time_label.setGeometry(15, 105, 80, 40)
        self.time_label.setStyleSheet(
            "QLabel {color: rgba(125,125,125,255); background-color: black;}"
        )
        self.time_label.setFont(canda_12)
        self.time_label.setText("Time:")
        self.time_label.hide()

        # Builds the "choice" label to display chosen appointment time
        self.choice_lbl = QLabel(self.frame1)
        self.choice_lbl.setGeometry(70, 105, 130, 40)
        self.choice_lbl.setStyleSheet(
            "QLabel {color: rgba(150,150,150,255); background-color: black;}"
        )
        self.choice_lbl.setFont(canda_12)
        self.choice_lbl.hide()

        # Builds the "place" label
        self.place_label = QLabel(self.frame1)
        self.place_label.setGeometry(15, 158, 80, 40)
        self.place_label.setStyleSheet(
            "QLabel {color: rgba(125,125,125,255); background-color: black;}"
        )
        self.place_label.setFont(canda_12)
        self.place_label.setText("Place:")
        self.place_label.hide()

        # Builds the "note" label
        self.note_label = QLabel(self.frame1)
        self.note_label.setGeometry(15, 240, 80, 40)
        self.note_label.setStyleSheet(
            "QLabel {color: rgba(125,125,125,255); background-color: black;}"
        )
        self.note_label.setFont(canda_12)
        self.note_label.setText("Note:")
        self.note_label.hide()

        # Builds the "list" widget for housing the "times" list
        self.listwidget = QListWidget(self.frame1)
        self.listwidget.setGeometry(100, 90, 100, 200)
        self.listwidget.resetVerticalScrollMode()
        self.listwidget.setFont(canda_10)
        self.listwidget.setStyleSheet(
            "QListWidget {color: rgba(125,125,125,255); background-color: black;}"
        )

        # Choice list for choosing appointment time
        times = [
            "All Day",
            "5:00 AM",
            "5:30 AM",
            "6:00 AM",
            "6:30 AM",
            "7:00 AM",
            "7:30 AM",
            "8:00 AM",
            "8:30 AM",
            "9:00 AM",
            "9:30 AM",
            "10:00 AM",
            "10:30 AM",
            "11:00 AM",
            "11:30 AM",
            "Noon",
            "12:30 PM",
            "1:00 PM",
            "1:30 PM",
            "2:00 PM",
            "2:30 PM",
            "3:00 PM",
            "3:30 PM",
            "4:00 PM",
            "4:30 PM",
            "5:00 PM",
            "5:30 PM",
            "6:00 PM",
            "6:30 PM",
            "7:00 PM",
        ]

        # This section iterates through the "times"
        # list and inserts them into a list widget.
        # variable "count" is used to prevent Index errors.
        count = 0
        for time in times:
            if count < len(times):
                self.listwidget.insertItem(count, time)
                count += 1
            else:
                pass
        self.listwidget.clicked.connect(self.choose) # Click on a time, perform the function "choose()".

        # Builds the "place" text input box
        self.place_edit = QTextEdit(self.frame1)
        self.place_edit.setGeometry(70, 155, 215, 60)
        self.place_edit.setStyleSheet(
            "QTextEdit {color: rgba(150,150,150,255); background-color: rgba(29, 29, 29, 150); border: none;}"
        )
        self.place_edit.setFont(canda_12)
        self.place_edit.hide()

        # Builds the "note" text input box
        self.note_edit = QTextEdit(self.frame1)
        self.note_edit.setGeometry(70, 235, 215, 80)
        self.note_edit.setStyleSheet(
            "QTextEdit {color: rgba(150,150,150,255); background-color: rgba(29, 29, 29, 150); border: none;}"
        )
        self.note_edit.setFont(canda_12)
        self.note_edit.hide()

        # Here, "format" is used to change color for the weekend days
        self.cal.setWeekdayTextFormat(Qt.Saturday, format)
        self.cal.setWeekdayTextFormat(Qt.Sunday, format)

        # Initiates and customizes the calendar
        self.cal.setGridVisible(False)
        self.cal.setGeometry(0, 0, 292, 221)
        self.cal.setFont(segoe_9)
        self.cal.setVerticalHeaderFormat(self.cal.NoVerticalHeader)
        self.cal.setStyleSheet(
            "QCalendarWidget QAbstractItemView{background-color: black;color: rgba(162,201,229,255);selection-background-color: rgb(30,30,30);selection-color: rgba(180, 180, 180, 250);selection-border: 1px solid black;}"
            "QCalendarWidget QWidget{alternate-background-color: rgb(20, 20, 20); color: gray;}"
            "QCalendarWidget QToolButton{background-color: black; color: rgb(125,125,125); font-size: 14px; font: bold; width: 70px;border: none;}"
            "QCalendarWidget QToolButton#qt_calendar_prevmonth{qproperty-icon: url(gif/left_arrow.png);}"
            "QCalendarWidget QToolButton#qt_calendar_nextmonth{qproperty-icon: url(gif/right_arrow.png);}"
        )
        self.cal.clicked[QDate].connect(self.showDate)

        symbol = u"\u2592" # My signature "EXIT" button symbol
        qtbutton(self, "exit", 280, 420, 20, 20, qdim, canda_11, symbol, self.exit)

        # Initiates and customizes the appointment table
        self.appt_table = QTableWidget(self)
        self.appt_table.setGeometry(QRect(20, 240, 257, 180))
        self.appt_table.setStyleSheet(
            "QTableWidget {color: rgb(56,95,220); background-color: rgb(10,10,10); border: none;"
            "alternate-background-color: black; border: none;}"
        )
        self.appt_table.horizontalHeader().hide()
        self.appt_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.appt_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.appt_table.setFont(canda_10)
        self.appt_table.setAlternatingRowColors(True)
        self.appt_table.verticalHeader().setVisible(False)

        # Appointment list to pandas df
        df = pd.DataFrame(self.appointments.appointments())
        self.display_data(df)

        # Timer updates appointment table every 2 seconds.
        # This way, an added appointment is displayed almost immediately.
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_table)
        self.update_table()
        self.show()

    # Opens the list widget for choosing appointment time
    def choose(self, qmodelindex):
        self.listwidget.show()
        choice = self.listwidget.currentItem()
        self.choice_lbl.setText(choice.text()) # Displays the chosen time
        self.place_label.show()
        self.choice_lbl.show()
        self.time_label.show()
        self.place_edit.show()
        self.note_label.show()
        self.listwidget.hide()
        self.note_edit.show()

    # Saves new appointment to the database
    def repeat(self):
        time  = self.listwidget.currentItem().text()
        place = self.place_edit.toPlainText()
        note  = self.note_edit.toPlainText()
        date  = self.date_data.text()[-10:][:5] #returns date formatted as '00-00-0000'

        mongo.insert_one({"date": date, "time": time, "place": place, "note": note})
        self.frame1.hide()

    # Update function for appointment table
    def update_table(self):
        df = pd.DataFrame(self.appointments.appointments())
        self.appt_table.update()
        self.cal.update()
        self.display_data(df)
        self.timer1.start(2000)
        self.update_table

    # Draws the line separators
    def paintEvent(self, e):
        self.painter = QPainter(self)
        self.painter.begin(self)
        self.painter.setPen(QColor(75, 75, 75))
        self.painter.drawLine(50, 230, 250, 230)
        self.painter.drawLine(50, 425, 250, 425)
        self.painter.end()

    # Sets up the appointment list display
    def display_data(self, var):
        self.appt_table.setColumnCount(len(var.columns))
        self.appt_table.setRowCount(len(var.index))

        for i in range(len(var.index)):
            for j in range(len(var.columns)):
                self.appt_table.setItem(i, j, QTableWidgetItem(str(var.iat[i, j])))
        self.appt_table.resizeColumnsToContents()

    # Takes selected date and creates the day name. The "if loop"
    # determines whether the selected date is a future date
    # (no sense in making an appointment for the past)
    def showDate(self, date):
        datx = self.cal.selectedDate()
        date = datx.toString("MM-dd-yyyy")
        self.cal.selectedDate().isNull()
        days = [
            "",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        dayo = QDate.dayOfWeek(datx)
        day = str(days[dayo])

        if str(date) < now.strftime("%m-%d-%Y"):
            pass
        else:
            self.event_form(date, day)

    # This function displays the newly formatted date calls the dock widget
    def event_form(self, date, day):
        self.date_data.setText(day + "  " + date)
        write_txt_file("string_date.txt", date, "w")

        self.items.setFeatures(QDockWidget.DockWidgetClosable)
        self.setCentralWidget(self.frame1)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.items)
        self.items.show()

    def close(self):
        self.frame1.hide()
        self.cal.show()

    def exit(self):
        sys.exit()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
