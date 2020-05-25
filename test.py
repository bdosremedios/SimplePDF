import unittest
from errors import *
from model import *
from tools import *


class testIDGenerator(unittest.TestCase):

    def testGenerateID(self):
        generator = IDGenerator()
        firstCode = generator.generateID()
        secondCode = generator.generateID()
        self.assertTrue(firstCode != secondCode)
        thirdCode = generator.generateID()
        self.assertTrue(thirdCode != firstCode)
        self.assertTrue(thirdCode != secondCode)


class testPDFPage(unittest.TestCase):

    def setUp(self):
        self.page1 = PDFPage('key1', None, None)
        self.page2 = PDFPage('key2', None, None)

    def testConstructor(self):
        self.assertTrue(self.page1.getID() != self.page2.getID())
        self.assertTrue(self.page1.getImage() is None)
        self.assertTrue(self.page1.getPageObject() is None)

    def testEq(self):
        self.assertTrue(self.page1 == self.page1)
        self.assertFalse(self.page1 == None)
        self.assertTrue(self.page1 == PDFPage(self.page1.getID(), None, None))


class testPDFPageBank(unittest.TestCase):

    def setUp(self):
        self.bank = PDFPageBank()
        self.page1 = PDFPage('key1', None, None)
        self.page2 = PDFPage('key2', None, None)

    def testConstructor(self):
        self.assertTrue(self.bank is not None)

    def testAddGetPage(self):
        self.bank.addPage(self.page1)
        self.bank.addPage(self.page2)
        self.assertEqual(self.bank.getPage(self.page1.getID()), self.page1)
        self.assertEqual(self.bank.getPage(self.page2.getID()), self.page2)

    def testAddSamePage(self):
        try:
            self.bank.addPage(self.page1)
            self.bank.addPage(self.page1)
            self.fail('Should have raised exception.')
        except(NotUniqueError):
            pass

    def testGetPageNotInBank(self):
        try:
            self.bank.getPage('notakey')
            self.fail('Should have raised exception.')
        except(NotInBankError):
            pass

    def testCountPages(self):
        self.assertEqual(self.bank.countPages(), 0)
        self.bank.addPage(self.page1)
        self.assertEqual(self.bank.countPages(), 1)
        self.bank.addPage(self.page2)
        self.assertEqual(self.bank.countPages(), 2)


class testPDF(unittest.TestCase):

    def setUp(self):
        self.bank = PDFPageBank()
        self.page1 = PDFPage('key1', None, None)
        self.page2 = PDFPage('key2', None, None)
        self.bank.addPage(self.page1)
        self.bank.addPage(self.page2)
        self.pdf = PDF(self.bank)

    def testConstructor(self):
        self.assertTrue(self.pdf is not None)
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2'])

    def testAddGetPage(self):
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        self.assertEqual(self.pdf.getPage(0), self.page1)
        self.assertEqual(self.pdf.getPage(1), self.page2)

    def testAddPageNotInBank(self):
        try:
            self.pdf.addPage(PDFPage('key3', None, None))
            self.fail('Should not have added PDFPage w key3 as is not in bank.')
        except(NotInBankError):
            pass

    def testCountPages(self):
        self.assertEqual(self.pdf.countPages(), 0)
        self.pdf.addPage(self.page1)
        self.assertEqual(self.pdf.countPages(), 1)
        self.pdf.addPage(self.page2)
        self.assertEqual(self.pdf.countPages(), 2)

    def test0LengthIterator(self):
        for page in self.pdf:
            self.fail('Nothing should have run in for loop since no elements.')

    def test2LengthIterator(self):
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        for page in self.pdf:
            pass
        iterable = iter(self.pdf)
        self.assertEqual(next(iterable), self.page1)
        self.assertEqual(next(iterable), self.page2)

    def testAppendEntirePDF(self):
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        pdf2 = PDF(self.bank)
        page3 = PDFPage('key3', None, None)
        page4 = PDFPage('key4', None, None)
        self.bank.addPage(page3)
        self.bank.addPage(page4)
        pdf2.addPage(page3)
        pdf2.addPage(page4)
        self.pdf.appendEntirePDF(pdf2)
        iterable = iter(self.pdf)
        self.assertEqual(next(iterable), self.page1)
        self.assertEqual(next(iterable), self.page2)
        self.assertEqual(next(iterable), page3)
        self.assertEqual(next(iterable), page4)

    def testAppendEntirePDFNotInBank(self):
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        otherBank = PDFPageBank()
        pdf2 = PDF(otherBank)
        page3 = PDFPage('key3', None, None)
        otherBank.addPage(page3)
        pdf2.addPage(page3)
        try:
            self.pdf.appendEntirePDF(pdf2)
            self.fail('Page3 not in bank so should have failed.')
        except(NotInBankError):
            pass

    def testRemovePage(self):
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        self.pdf.removePage(1)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1'])
        self.pdf.addPage(self.page2)
        self.pdf.removePage(0)
        self.assertEqual(self.pdf._getOrderedPages(), ['key2'])

    def testRemovePageBadIndex(self):
        try:
            self.pdf.removePage(0)
            self.fail('No items yet so should not be able to remove anything.')
        except(IndexError):
            pass

    def MoveTestSetUp(self):
        self.page3 = PDFPage('key3', None, None)
        self.page4 = PDFPage('key4', None, None)
        self.bank.addPage(self.page3)
        self.bank.addPage(self.page4)
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        self.pdf.addPage(self.page3)
        self.pdf.addPage(self.page4)

    def testMoveBeforePage(self):
        # Test move middle item to same place both ways
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(1, 2)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(1, 1)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])

        # Test move middle item before end element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(1, 3)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key3', 'key2', 'key4'])

        # Test move middle item before first element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(1, 0)
        self.assertEqual(self.pdf._getOrderedPages(), ['key2', 'key1', 'key3', 'key4'])

        # Test move first item before end element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(0, 3)
        self.assertEqual(self.pdf._getOrderedPages(), ['key2', 'key3', 'key1', 'key4'])

        # Test move first item before first element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(0, 0)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])

        # Test move last item before end element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(3, 3)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])

        # Test move last item before first element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveBeforePage(3, 0)
        self.assertEqual(self.pdf._getOrderedPages(), ['key4', 'key1', 'key2', 'key3'])

    def testMoveAfterPage(self):
        # Test move middle item to same place both ways
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(1, 0)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(1, 1)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])

        # Test move middle item after end element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(1, 3)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key3', 'key4', 'key2'])

        # Test move middle item after third element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(1, 2)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key3', 'key2', 'key4'])

        # Test move first item after end element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(0, 3)
        self.assertEqual(self.pdf._getOrderedPages(), ['key2', 'key3', 'key4', 'key1'])

        # Test move first item after first element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(0, 0)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])

        # Test move last item after end element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(3, 3)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key2', 'key3', 'key4'])

        # Test move last item after first element
        self.setUp()
        self.MoveTestSetUp()
        self.pdf.moveAfterPage(3, 0)
        self.assertEqual(self.pdf._getOrderedPages(), ['key1', 'key4', 'key2', 'key3'])

    def testEq(self):
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        self.assertTrue(self.pdf == self.pdf)
        self.assertFalse(self.pdf == None)
        pdf2 = PDF(self.bank)
        pdf2.addPage(self.page1)
        pdf2.addPage(self.page2)
        self.assertTrue(self.pdf == pdf2)
        pdf2.removePage(1)
        self.assertFalse(self.pdf == pdf2)

    def testCopyPDF(self):
        self.pdf.addPage(self.page1)
        self.pdf.addPage(self.page2)
        pdf2 = self.pdf.copyPDF()
        self.assertEqual(pdf2, self.pdf)
        self.assertFalse(pdf2 is self.pdf)


class testPDFHistoryRecorder(unittest.TestCase):

    def setUp(self):
        self.bank = PDFPageBank()
        self.page1 = PDFPage('key1', None, None)
        self.page2 = PDFPage('key2', None, None)
        self.page3 = PDFPage('key3', None, None)
        self.page4 = PDFPage('key4', None, None)
        self.bank.addPage(self.page1)
        self.bank.addPage(self.page2)
        self.bank.addPage(self.page3)
        self.bank.addPage(self.page4)
        self.pdf = PDF(self.bank)
        self.pdf2 = PDF(self.bank)
        self.pdf3 = PDF(self.bank)
        self.historyRecorder = PDFHistoryRecorder()

    def testConstructor(self):
        self.assertTrue(self.historyRecorder is not None)

    def testNewVersion(self):
        self.historyRecorder.newVersion(self.pdf)
        self.assertEqual(self.historyRecorder._getCurrentVersion(), 0)
        self.pdf.addPage(self.page1)
        self.historyRecorder.newVersion(self.pdf)
        self.assertEqual(self.historyRecorder._getCurrentVersion(), 1)
        self.pdf.addPage(self.page2)
        self.historyRecorder.newVersion(self.pdf)
        self.assertEqual(self.historyRecorder._getCurrentVersion(), 2)
        self.pdf.removePage(1)
        self.historyRecorder.newVersion(self.pdf)
        self.assertEqual(self.historyRecorder._getCurrentVersion(), 3)
        versions = self.historyRecorder._getVersions()
        self.assertEqual(len(versions), 4)
        self.assertEqual(versions[3], self.pdf)
        self.pdf.addPage(self.page2)
        self.assertEqual(versions[2], self.pdf)
        self.pdf.removePage(1)
        self.assertEqual(versions[1], self.pdf)
        self.pdf.removePage(0)
        self.assertEqual(versions[0], self.pdf)

    def testNewVersionRemoveLaterVersions(self):
        self.historyRecorder.newVersion(self.pdf)
        self.pdf.addPage(self.page1)
        self.historyRecorder.newVersion(self.pdf)
        self.pdf.addPage(self.page2)
        self.historyRecorder.newVersion(self.pdf)
        self.pdf.removePage(1)
        self.historyRecorder.newVersion(self.pdf)
        self.historyRecorder._setCurrentVersion(1)
        self.historyRecorder.newVersion(self.pdf)
        versions = self.historyRecorder._getVersions()
        self.assertEqual(versions[-1], self.pdf)
        self.assertEqual(versions[-2], self.pdf)
        self.pdf.removePage(0)
        self.assertEqual(versions[-3], self.pdf)

    def addVersionsToRecorder(self):
        self.pdf.addPage(self.page1)
        self.pdf2.addPage(self.page1)
        self.pdf2.addPage(self.page2)
        self.pdf3.addPage(self.page2)
        self.historyRecorder.newVersion(self.pdf)
        self.historyRecorder.newVersion(self.pdf2)
        self.historyRecorder.newVersion(self.pdf3)

    def testPreviousVersion(self):
        self.addVersionsToRecorder()
        self.assertEqual(self.historyRecorder.previousVersion(), self.pdf2)
        self.assertEqual(self.historyRecorder.previousVersion(), self.pdf)
        try:
            self.historyRecorder.previousVersion()
            self.fail('Should throw exception as no more previous versions.')
        except(NoPrevVersions):
            pass

    def testLaterVersion(self):
        self.addVersionsToRecorder()
        self.historyRecorder._setCurrentVersion(0)
        self.assertEqual(self.historyRecorder.laterVersion(), self.pdf2)
        self.assertEqual(self.historyRecorder.laterVersion(), self.pdf3)
        try:
            self.historyRecorder.laterVersion()
            self.fail('Should throw exception as no more future versions.')
        except(NoLaterVersions):
            pass


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)