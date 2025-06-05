# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'auto_upload.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(532, 568)
        self.verticalLayoutWidget = QWidget(Form)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 511, 545))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.id = QLineEdit(self.verticalLayoutWidget)
        self.id.setObjectName(u"id")

        self.gridLayout.addWidget(self.id, 0, 1, 1, 1)

        self.password = QLineEdit(self.verticalLayoutWidget)
        self.password.setObjectName(u"password")

        self.gridLayout.addWidget(self.password, 1, 1, 1, 1)

        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.label_3 = QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.github = QRadioButton(self.verticalLayoutWidget)
        self.github.setObjectName(u"github")

        self.horizontalLayout.addWidget(self.github)

        self.google = QRadioButton(self.verticalLayoutWidget)
        self.google.setObjectName(u"google")

        self.horizontalLayout.addWidget(self.google)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.not_upload_files_dirs = QLineEdit(self.verticalLayoutWidget)
        self.not_upload_files_dirs.setObjectName(u"not_upload_files_dirs")

        self.gridLayout_2.addWidget(self.not_upload_files_dirs, 0, 1, 1, 1)

        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QSize(140, 0))
        self.label_4.setMaximumSize(QSize(120, 16777215))

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)

        self.not_upload_btn = QPushButton(self.verticalLayoutWidget)
        self.not_upload_btn.setObjectName(u"not_upload_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.not_upload_btn.sizePolicy().hasHeightForWidth())
        self.not_upload_btn.setSizePolicy(sizePolicy1)
        self.not_upload_btn.setMinimumSize(QSize(10, 0))
        self.not_upload_btn.setMaximumSize(QSize(30, 16777215))

        self.gridLayout_2.addWidget(self.not_upload_btn, 0, 2, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.verticalLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(140, 0))

        self.horizontalLayout_3.addWidget(self.label_5)

        self.upload_files_dirs = QLineEdit(self.verticalLayoutWidget)
        self.upload_files_dirs.setObjectName(u"upload_files_dirs")

        self.horizontalLayout_3.addWidget(self.upload_files_dirs)

        self.upload_btn = QPushButton(self.verticalLayoutWidget)
        self.upload_btn.setObjectName(u"upload_btn")
        self.upload_btn.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout_3.addWidget(self.upload_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.write_btn = QPushButton(self.verticalLayoutWidget)
        self.write_btn.setObjectName(u"write_btn")

        self.verticalLayout.addWidget(self.write_btn)

        self.scrollArea = QScrollArea(self.verticalLayoutWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.logs = QWidget()
        self.logs.setObjectName(u"logs")
        self.logs.setGeometry(QRect(0, 0, 507, 298))
        self.scrollArea.setWidget(self.logs)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\ube44\ubc00\ubc88\ud638 : ", None))
        self.label.setText(QCoreApplication.translate("Form", u"\uc544\uc774\ub514 : ", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\ub85c\uadf8\uc778 \ubc29\uc2dd", None))
        self.github.setText(QCoreApplication.translate("Form", u"\uae43\ud5c8\ube0c", None))
        self.google.setText(QCoreApplication.translate("Form", u"\uad6c\uae00", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\uc5c5\ub85c\ub4dc\ud560 \ucf54\ub4dc\ub4e4", None))
        self.not_upload_btn.setText(QCoreApplication.translate("Form", u"...", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\uc5c5\ub85c\ub4dc\ub97c \ub05d\ub0b8 \ucf54\ub4dc\ub4e4", None))
        self.upload_btn.setText(QCoreApplication.translate("Form", u"...", None))
        self.write_btn.setText(QCoreApplication.translate("Form", u"\uae00\uc4f0\uae30", None))
    # retranslateUi

