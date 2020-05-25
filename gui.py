import os
import re
import matplotlib.pyplot as plt
from errors import *
from model import *
from tools import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PIL import Image, ImageOps
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class selectFileGUI(QDialog):
    """
    GUI serving as file selection dialog. Slightly generalized such that it could be inherited to be used as a folder
    selector too to save code (Less elegant as less directly focused in a way but better as it reduces coupling).

    """
    def __init__(self, title='Select PDF to Edit', browseButtonName='Browse', finishSelectionButtonName='Select PDF'):
        super().__init__()
        self._setUI(title, browseButtonName, finishSelectionButtonName)
        self.selectedPDFPath = None  # sets selectedPDFPath as none initially
        self.exec_()
        self.raise_()
        self.activateWindow()
        self.move(int(QDesktopWidget().availableGeometry().center().x()-self.width()/2.),
                  int(QDesktopWidget().availableGeometry().center().y()-self.height()/2.))

    def _setUI(self, title, browseButtonName, finishSelectionButtonName):
        """
        Sets buttons and line edit widgets in main QDialog.

        """
        self.setWindowTitle(title)
        layout = QGridLayout()

        self.fileName = QLineEdit()
        layout.addWidget(self.fileName, 0, 0, 1, 2)

        self.browse = QPushButton(browseButtonName)
        self.browse.clicked.connect(lambda: self._handleFileDialog(self.fileName))
        layout.addWidget(self.browse, 0, 2)

        self.editPDF = QPushButton(finishSelectionButtonName)
        self.editPDF.clicked.connect(lambda: self._handleEditPDFButton(self.fileName.text()))
        layout.addWidget(self.editPDF, 1, 0)

        self.setLayout(layout)

    def _handleFileDialog(self, qLineEdit):
        """
        Opens QFileDialog and changes qLineEdit text to file selected.

        """
        dialog = QFileDialog()
        dialog.open(lambda: qLineEdit.setText(dialog.selectedFiles()[0]))
        dialog.exec_()

    def _handleEditPDFButton(self, fileName):
        """
        Checks fileName to see if is pdf file and that it exists, opening error dialog if not.

        Parameters
        ---
        fileName : str
            fileName to check for validity

        """
        errorText = ''
        if (re.fullmatch('.*\.pdf/?', fileName) is None):
            errorText += 'File must be pdf.\n'
        if (not os.path.isfile(fileName)):
            errorText += 'File does not exist.\n'
        if errorText != '':
            errorBox = QMessageBox()
            errorBox.setWindowTitle('File Error')
            errorBox.setText(errorText)
            errorBox.setIcon(QMessageBox.Warning)
            errorBox.exec_()
        else:
            self.selectedPDFPath = fileName
            self.close()

    def getSelectedPDFPath(self):
        """
        Gets the finalized selected path after the GUI is closed, if none is set raises an exception.

        Raises
        ---
        NoValidFilePathGiven
            Thrown when during application's lifetime no valid filepath was selected.

        """
        if self.selectedPDFPath is not None:
            return(self.selectedPDFPath)
        else:
            raise(NoValidFilePathGiven('No valid path was given during application lifetime.'))


class createSavePathGUI(selectFileGUI):
    """
    selectFileGUI with altered button names and handleFileName check behavior change.

    """
    def __init__(self):
        super().__init__('Create save path', 'Save as', 'OK')

    # Override
    def _handleEditPDFButton(self, fileName):
        """
        Checks fileName to see if is valid save path and that it exists, opening error dialog if not.

        Parameters
        ---
        fileName : str
            fileName to check for validity

        """
        errorText = ''
        head, tail = os.path.split(fileName)
        if (re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9 ]*[a-zA-Z0-9](\.pdf)?', tail) is None):
            errorText += 'File name not valid.\n'
        if (not os.path.isdir(head)):
            errorText += 'Storage directory not valid or does not exist.\n'
        if errorText != '':
            errorBox = QMessageBox()
            errorBox.setWindowTitle('File Error')
            errorBox.setText(errorText)
            errorBox.setIcon(QMessageBox.Warning)
            errorBox.exec_()
        else:
            self.selectedPDFPath = fileName
            if (re.fullmatch('.*\.pdf', tail) is None):
                self.selectedPDFPath += '.pdf'  # add pdf extension to fileName if not there
            self.close()


class editFileGUI(QDialog):
    """
    Main GUI used to edit PDF, capable of appending a PFD, removing/moving pages, undo/redo, and saving the edited PDF.

    """
    def __init__(self, pdfFilePath):
        super().__init__()

        # Create single bank and IDgenerator for instance of GUI
        self.bank = PDFPageBank()
        self.generator = IDGenerator()
        self.recorder = PDFHistoryRecorder()
        self.pdf = self.loadPDF(pdfFilePath)
        self.moveMode = False  # Not initially in moveMode
        self.currentIndex = 0
        self.pageCount = self.pdf.countPages()

        # Load UI
        self._setUI()
        self._update()
        self.exec_()

    def _setUI(self):
        """
        Sets buttons and main canvas in main QDialog.

        """
        self.setWindowTitle('SimplePDF')
        layout = QGridLayout()

        # Add main figure
        self.mainFigure, self.mainAx = plt.subplots(figsize=(6, 7.75))
        self.mainAx.tick_params(axis='both', left=False, bottom=False, labelleft=False, labelbottom=False)
        self.mainFigure.tight_layout(pad=0)
        self.canvas = FigureCanvasQTAgg(self.mainFigure)
        layout.addWidget(self.canvas, 1, 1, 7, 3)

        # Main figure arrows, current index, and select page button
        self.prevPageButton = QPushButton('<')
        self.prevPageButton.clicked.connect(lambda: self._incrementPageIndex(-1))
        layout.addWidget(self.prevPageButton, 4, 0)

        self.nextPageButton = QPushButton('>')
        self.nextPageButton.clicked.connect(lambda: self._incrementPageIndex(1))
        layout.addWidget(self.nextPageButton, 4, 4)

        self.indexDisplay = QLabel('')
        self.indexDisplay.setAlignment(Qt.AlignCenter)
        self.indexDisplay.setFont(QFont('default', 11))
        layout.addWidget(self.indexDisplay, 0, 2)

        self.placeBeforeButton = QPushButton('Place Before')
        self.placeBeforeButton.clicked.connect(lambda: self._movePage('Before'))
        self.placeBeforeButton.setEnabled(False)
        layout.addWidget(self.placeBeforeButton, 8, 1)

        self.placeAfterButton = QPushButton('Place After')
        self.placeAfterButton.clicked.connect(lambda: self._movePage('After'))
        self.placeAfterButton.setEnabled(False)
        layout.addWidget(self.placeAfterButton, 8, 2)

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(lambda: self._cancelMovePage())
        self.cancelButton.setEnabled(False)
        layout.addWidget(self.cancelButton, 8, 3)

        # Function buttons append, remove page, move page, undo, redo, export
        self.appendPDFButton = QPushButton('Append PDF')
        self.appendPDFButton.clicked.connect(lambda: self._handleAppendPDF())
        layout.addWidget(self.appendPDFButton, 2, 5, 1, 2)

        self.removePageButton = QPushButton('Remove Page')
        self.removePageButton.clicked.connect(lambda: self._removeCurrentPage())
        layout.addWidget(self.removePageButton, 3, 5, 1, 2)

        self.movePageButton = QPushButton('Move Page')
        self.movePageButton.clicked.connect(lambda: self._handleMovePage())
        layout.addWidget(self.movePageButton, 4, 5, 1, 2)

        self.undoButton = QPushButton('Undo')
        self.undoButton.clicked.connect(lambda: self._handleVersionChange('Undo'))
        layout.addWidget(self.undoButton, 5, 5)

        self.redoButton = QPushButton('Redo')
        self.redoButton.clicked.connect(lambda: self._handleVersionChange('Redo'))
        layout.addWidget(self.redoButton, 5, 6)

        self.exportPDFButton = QPushButton('Export PDF')
        self.exportPDFButton.clicked.connect(lambda: self._handleExportPDF())
        layout.addWidget(self.exportPDFButton, 6, 5, 1, 2)

        self.setLayout(layout)

    # Override
    def closeEvent(self, event):
        plt.close('all')
        self.close()

    def loadPDF(self, pdfFilePath):
        """
        Returns PDF of the given pdf at pdfFilePath.

        """
        converter = File2PDFConverter(pdfFilePath, self.generator, self.bank)
        return(converter.extractPDF())

    def _update(self):
        """
        Saves current version of pdf and updates all UI. Use whenever there is a change to pdf.

        """
        self._saveVersion()
        self._updateUI()

    def _updateUI(self):
        """
        Updates pageCount and displayed page count, current index, and main figure to current one of PDF.

        """
        self.pageCount = self.pdf.countPages()
        self.indexDisplay.setText('{}/{}'.format(self.currentIndex+1, self.pageCount))
        self.mainAx.clear()
        if self.moveMode and (self.currentIndex == self.indexToMove):
            self.mainAx.imshow(ImageOps.colorize(ImageOps.grayscale(self.pdf.getPage(self.currentIndex).getImage()),
                                                 black='#000000', white='#add8e6'))
        else:
            self.mainAx.imshow(self.pdf.getPage(self.currentIndex).getImage())
        self.canvas.draw()

    def _saveVersion(self):
        """
        Saves current pdf as new version in recorder.

        """
        self.recorder.newVersion(self.pdf)

    def _incrementPageIndex(self, i):
        """
        If increment does not bring page count under 0 or over pageCount-1, increment i pages and update UI.

        """
        if 0 <= self.currentIndex+i <= self.pageCount-1:
            self.currentIndex += i
            self._updateUI()

    def _handleAppendPDF(self):
        """
        Adds given PDF to the end of current PDF, doing nothing if there isn't a PDF given.

        """
        gui = selectFileGUI('Select PDF to Append')
        try:
            self.pdf.appendEntirePDF(self.loadPDF(gui.getSelectedPDFPath()))
            self._update()
        except(NoValidFilePathGiven):
            pass

    def _removeCurrentPage(self):
        """
        If there is still more then one page, deletes current page and moves to previous. If already at first page
        does not move.

        """
        if self.pageCount > 1:
            self.pdf.removePage(self.currentIndex)
            if self.currentIndex > 0:
                self.currentIndex -= 1
            self._update()

    def _handleMovePage(self):
        """
        Initiates move page function version of GUI. Records index of page to move and changes to move mode.

        """
        self.indexToMove = self.currentIndex
        self._activateMoveFunction(True)
        self._updateUI()

    def _cancelMovePage(self):
        """
        Changes to regular edit mode from move mode.

        """
        self._activateMoveFunction(False)
        self._updateUI()

    def _movePage(self, movement):
        """
        Moves page to before or after the current indexed page depending on movement given. Changes index so that it remains
        on current page despite change.

        """
        if movement == 'Before':
            self.pdf.moveBeforePage(self.indexToMove, self.currentIndex)
            if self.indexToMove > self.currentIndex:
                self.currentIndex += 1
        elif movement == 'After':
            self.pdf.moveAfterPage(self.indexToMove, self.currentIndex)
            if self.indexToMove < self.currentIndex:
                self.currentIndex -= 1
        self._activateMoveFunction(False)
        self._update()

    def _activateMoveFunction(self, boolean):
        """
        Activates or deactivates move mode which entails setting certain move buttons enabled or disabled, and everything
        else opposite to that state, so only moving or only not moving is option in GUI.

        """
        self.moveMode = boolean
        self.appendPDFButton.setEnabled(not boolean)
        self.removePageButton.setEnabled(not boolean)
        self.movePageButton.setEnabled(not boolean)
        self.undoButton.setEnabled(not boolean)
        self.redoButton.setEnabled(not boolean)
        self.exportPDFButton.setEnabled(not boolean)
        self.placeBeforeButton.setEnabled(boolean)
        self.placeAfterButton.setEnabled(boolean)
        self.cancelButton.setEnabled(boolean)

    def _handleVersionChange(self, change):
        """
        Moves to previous or later version of PDF depending on change value, and does nothing if there is no version to change
        to. Updates index so that it does not go beyond the page maximum.

        """
        if change == 'Undo':
            try:
                self.pdf = self.recorder.previousVersion()
            except(NoPrevVersions):
                pass
        elif change == 'Redo':
            try:
                self.pdf = self.recorder.laterVersion()
            except(NoLaterVersions):
                pass
        if self.currentIndex > self.pdf.countPages()-1:  # Set to last page if current Index is beyond
            self.currentIndex = self.pdf.countPages()-1
        self._updateUI()

    def _handleExportPDF(self):
        """
        Opens a GUI to create a save file name and creates a file there if given one. Does nothing if not.

        """
        gui = createSavePathGUI()
        try:
            converter = PDF2FileConverter(self.pdf)
            converter.extractToFilePath(gui.getSelectedPDFPath())
        except(NoValidFilePathGiven):
            pass

