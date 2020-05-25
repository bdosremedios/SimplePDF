from PyQt5.QtWidgets import *
from gui import *

if __name__ == '__main__':
    # var assignment prevents garbage collection
    app = QApplication([])
    gui = selectFileGUI()
    try:
        main = editFileGUI(gui.getSelectedPDFPath())
    except(NoValidFilePathGiven):
        pass