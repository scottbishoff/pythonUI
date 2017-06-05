# -*- coding: utf-8 -*-
"""
Created on Tue May 02 10:36:07 2017
Python 2.7.13 |Anaconda 4.3.1 (64-bit)| (default, Dec 19 2016, 13:29:36) [MSC v.1500 64 bit (AMD64)]
Author: Scott Bishoff
"""

import sys
import getpass
import json
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QMessageBox, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5 import QtGui
import DetectPorts

#This class defines the GUI
class MainWindow(QWidget):
    #__init__ will run whenever MainWindow() is called
    def __init__(self, parent=None):
            self.arduino = serial.Serial(DetectPorts.findPort(), 9600, timeout=10)
            super(MainWindow, self).__init__(parent)
            self.resize(700,200)
            self.setWindowTitle('Mini Wye Test')
            self.setWindowIcon(QtGui.QIcon('TDW_logo.png'))
            self.initUI()
            self.failure_results = 'The following tests failed: \n'    

    #this defines all of the GUI components
    def initUI(self):
        self.btnStartTest = QPushButton('Start',self) 
        self.btnViewDetails = QPushButton('View Detailed Results')
        self.btnViewDetails.hide()
        
        self.txtInfo = QTextEdit(self)
        self.txtInfo.setFixedHeight(250)       
        self.txtInfo.move(0,200)       
        self.txtStatus = QLabel('Connected to Teensy on %s' % DetectPorts.findPort(),self)
        self.txtStatus.setFixedWidth(200)        
                    
        h_box = QHBoxLayout()
        h_box.addWidget(self.btnStartTest)
        h_box.addStretch()
        h_box.addWidget(self.btnViewDetails)
        
        v_box = QVBoxLayout()
        v_box.addWidget(self.txtStatus)
        v_box.addLayout(h_box)
        v_box.addWidget(self.txtInfo)
                     
        self.setLayout(v_box)
        
        self.btnStartTest.clicked.connect(self.show_status)  
        self.btnViewDetails.clicked.connect(self.view_results)
       
    def show_status(self):
        self.txtInfo.setFontPointSize(40)
        self.txtInfo.setText('Running test........')
        self.txtInfo.setStyleSheet('background-color:white')
        QApplication.processEvents()
        self.btn_click()
        
    #runs when the start button is pushed.     
    def btn_click(self):
        self.failure_results = 'The following tests failed: \n' #Reset the string which keeps track of failure info
        try:            
            self.arduino.write('r')
            self.data = self.arduino.readline()
            self.parsed_json = json.loads(self.data)#Convert data received to json
            self.txtInfo.setFontPointSize(40)    
            if self.parsed_json["passed"]:
                testResults = "The test PASSED"
                self.txtInfo.setStyleSheet("background-color:green")
            else:
                testResults = "The test FAILED"
                self.txtInfo.setStyleSheet("background-color:red")
           
#            txt_file = open("json.txt", "w")
#            txt_file.write(str(json.dumps(self.parsed_json, indent=4, sort_keys=True)))
#            txt_file.close()
            print self.parsed_json
            self.txtInfo.setText(testResults)
            self.txtInfo.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.btnViewDetails.show()#show the view results button only after data has been received
            self.find_failed_test(self.parsed_json,"")
            
        except Exception as e:
            print e.__doc__
            print e.message
            
    #Change the info box to show the detailed information about the pass/failure
    def view_results(self):        
        self.txtInfo.setFontPointSize(8)
        self.txtInfo.setText(self.failure_results)
        self.txtInfo.setStyleSheet("background-color:white")
    
    def find_failed_test(self, result, parent_name):  
        #Recursive function that loops through every dictionary and pulls the information for all tests
        #that failed
        for key, values in result.iteritems():
            if isinstance(values, dict):
                self.find_failed_test(values, parent_name + result['testName'] + ", ")
                return
            elif isinstance(values, list):
                for v in values:
                    self.find_failed_test(v, parent_name + result['testName'] + ", ")
                return
            
        if not result['passed']:
            self.failure_results += (parent_name + str(result['testName']) +':'+ str(result['data']) + '\n')
            
            
           
#Defines an error message if the application is run and there isn't an arduino
#detected, if so, the application will close. 
def showError():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("No test fixture detected. Please ensure the test fixture is plugged into one of the USB ports.")
    msg.setWindowTitle("Error Connecting")   
    msg.setStandardButtons(QMessageBox.Ok)  	
    msg.exec_()
    sys.exit()
   

def main():        
    try:
        #Checks if there is already a QCoreApplication running.
        userName = getpass.getuser() #get the username of the person logged in. 
        if QCoreApplication.instance() != None:
            app = QCoreApplication.instance()
        else:
            app = QApplication(sys.argv)    
        if DetectPorts.findPort() == None: #Check to see if there is a Teensy connected
            showError()
        else: 
            window = MainWindow()
            window.show()            
            sys.exit(app.exec_())
    finally:
        window.arduino.close() #close the arduino connection if it is still open
        sys.exit()   


if __name__ == "__main__":
    main()
