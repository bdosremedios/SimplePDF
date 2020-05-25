import re
import PyPDF2
from errors import *
from model import *
from pdf2image import convert_from_path

class IDGenerator():
    """
    Creates a unique str id to current IDGenerator object's knowledge.

    Attributes
    ---
    nextID : int
        Next identifier the generator will output
    """
    def __init__(self):
        self.nextID = 0

    def generateID(self):
        """
        Returns a string of unique int id and updates nextID to new unique ID.

        """
        stringCode = str(self.nextID)
        self.nextID += 1
        return(stringCode)


class File2PDFConverter():
    """
    Object that extracts a vaild pdf file into a PDF object.

    Attributes
    ---
    reader : PyPDF2.PDFFileReader
        Object to read in actual pdf file and extract PyPDF2.pageObjects to put into
        actual pdf file later.
    images : list <PIL.PpmImagePlugin.PpmImageFile>
        PpmImageFile of page for graphical display in same order as pages in reader.
    generator : IDGenerator
        IDGenerator for application to generate unique IDs for created PDFPages.
    pdfBank : PDFPageBank
        PDFPageBank to store PDFPages for, for all PDFs.

    """
    def __init__(self, filePath, idGenerator, pdfBank):
        self.reader = PyPDF2.PdfFileReader(filePath)
        self.images = convert_from_path(filePath)
        self.generator = idGenerator
        self.bank = pdfBank

    def extractPDF(self):
        """
        Extracts and returns PDF object of given filePath

        Returns
        ---
        PDF
             PDF containing ordered pages in same form as PDF from filePath
        """
        pdf = PDF(self.bank)
        for i in range(self.reader.getNumPages()):
            page = PDFPage(self.generator.generateID(),
                           self.images[i],
                           self.reader.getPage(i))
            self.bank.addPage(page)
            pdf.addPage(page)
        return(pdf)


class PDF2FileConverter():
    """
    Object that converts a PDF object into an actual pdf file.

    Attributes
    ---
    writer : PyPDF2.PdfFileWriter
        Object that actually extracts out pdf.

    """
    def __init__(self, pdf):
        self.writer = PyPDF2.PdfFileWriter()
        for page in pdf:
            self.writer.addPage(page.getPageObject())

    def extractToFilePath(self, filePath):
        """
        Extracts PDF that is loaded in writer, into a pdf file at filePath.

        Parameters
        ---
        filePath : str
            String of file path to create pdf file with.

        """
        if (re.fullmatch('.*\.pdf?', filePath) is not None):
            fileStream = open(filePath, 'wb')
            self.writer.write(fileStream)
            fileStream.close()
        else:
            raise(FilePathNotPDF('Given file path must be valid pdf file (No end slash also).'))

