from errors import *


class PDFPage():
    """
    PDF Page containing both image and PyPDF2 page representation of PDF.

    Attributes
    ---
    ID : str
        ID identifying object.
    image : PIL.PpmImagePlugin.PpmImageFile
        PpmImageFile of page for graphical display.
    pageObject : PyPDF2.page.PageObject
        PageObject of pypdf2 page for actually making pdf.

    """
    def __init__(self, ID, image, pageObject):
        self.ID = ID
        self.image = image
        self.pageObject = pageObject

    def __eq__(self, obj):
        if obj is self:
            return(True)
        elif not isinstance(obj, PDFPage):
            return(False)
        else:
            return((obj.getID() == self.getID()) and
                   (obj.getImage() == self.getImage()) and
                   (obj.getPageObject() == self.getPageObject()))

    def getID(self):
        return(self.ID)

    def getImage(self):
        return(self.image)

    def getPageObject(self):
        return(self.pageObject)


class PDFPageBank():
    """
    Bank of all PDFPages added so far.

    Attributes
    ---
    map : dict
        Dictionary of pdfPages with key of PDFPage's ID and value of PDFPage.

    """
    def __init__(self):
        self.map = {}

    def contains(self, ID):
        """
        Returns true if pdfPage ID is in page bank.
        
        Parameters
        ---
        ID : str
            ID to check if in.
        
        Returns
        ---
        bool
            True if is in, false otherwise.
        
        """
        return(ID in self.map.keys())

    def addPage(self, pdfPage):
        """
        Adds pdfPage to dictionary with its ID as its key.
        
        Parameters
        ---
        pdfPage : PDFPage
            PDFPage to add to bank.
            
        Raises
        ---
        NotUniqueError
            Raised if pdfPage with matching key is already added to bank.
            
        """
        if not self.contains(pdfPage.getID()):
            self.map[pdfPage.getID()] = pdfPage
        else:
            raise NotUniqueError('PDFPage exists in PDFPageBank already.')


    def getPage(self, ID):
        """
        Gets pdfPage with corresponding ID.

        Parameters
        ---
        ID : str
            ID of page to get.

        Returns
        ---
        PDFPage
            Page with matching ID.

        Raises
        ---
        NotInBankError
            Raised if no page has a matching ID.

        """
        if self.contains(ID):
            return(self.map.get(ID))
        else:
            raise NotInBankError('No PDFPage with given ID in Bank.')

    def countPages(self):
        """
        Returns int of number of pages in bank.

        """
        return(len(self.map.keys()))


class PDF():
    """
    Ordered collection of References to PDFPage IDs in PDFPageBank.

    Attributes
    ---
    orderedPages : list
        List of ordered PDFPage IDs representing PDF.
    pageBank : PDFPageBank
        PDFPageBank where PDFPages in PDF are located.

    Notes
    ---
    Iterable of PDFPage.

    """
    def __init__(self, pageBank):
        self.orderedPages = []
        self.pageBank = pageBank

    def __eq__(self, obj):
        if obj is self:
            return(True)
        elif not isinstance(obj, PDF):
            return(False)
        else:
            return((obj._getOrderedPages() == self.orderedPages))

    def __iter__(self):
        self.currentIndex = 0
        return(self)

    def __next__(self):
        if self.currentIndex  < self.countPages():
            page = self.getPage(self.currentIndex)
            self.currentIndex += 1
            return(page)
        else:
            raise(StopIteration)

    def _setOrderedPages(self, orderedPages):
        self.orderedPages = orderedPages

    def _getOrderedPages(self):
        return(self.orderedPages)

    def addPage(self, pdfPage):
        """
        Adds PDFPage Object to end of PDF if is in pageBank.

        Parameters
        ---
        pdfPage : PDFPage
            PDFPage to add to bank.

        Raises
        ---
        NotInBankError
            Raised if pdfPage not in bank yet.

        """
        if self.pageBank.contains(pdfPage.getID()):
            self.orderedPages.append(pdfPage.getID())
        else:
            raise(NotInBankError("PDFPage not in pagebank."))

    def getPage(self, i):
        """
        Returns reference to pdfPage of index i from PDF, grabbed from page bank. 

        """
        return(self.pageBank.getPage(self.orderedPages[i]))

    def removePage(self, i):
        """
        Removes page at index i from PDF. 

        """
        self.orderedPages.pop(i)

    def moveBeforePage(self, i, beforeThisIndex):
        """
        Moves page at index i in front of page at beforeThisIndex.

        """
        self.orderedPages = (self.orderedPages[:beforeThisIndex] + 
                             [self.orderedPages[i]] +  # Page to reinsert
                             self.orderedPages[beforeThisIndex:])  # Slice including beforeThisIndex
        if i < beforeThisIndex:  # Just removes item at old index since that is same original
            self.removePage(i)
        else:  # Removes item at old index+1, since old item would have been shifted by one if >= original i
            self.removePage(i+1)

    def moveAfterPage(self, i, afterThisIndex):
        """
        Moves page at index i after page at afterThisIndex.

        """
        self.orderedPages = (self.orderedPages[:afterThisIndex+1] +  # Slice including afterThisIndex
                             [self.orderedPages[i]] +  # Page to reinsert
                             self.orderedPages[afterThisIndex+1:])
        if i >= afterThisIndex:  # Removes item at old index+1, since old item would have been shifted by one if moving page is > afterThisIndex
            self.removePage(i+1)
        else:  # Just removes item at old index since that is same original
            self.removePage(i)

    def countPages(self):
        """
        Returns int of number of pages in PDF.

        """
        return(len(self.orderedPages))

    def appendEntirePDF(self, pdf):
        """
        Appends all pages in pdf to the end of self.

        Raises
        ---
        NotInBankError
            Raised if any pages in pdf are not in the same bank as this pdf.

        """
        for page in pdf:
            self.addPage(page)

    def copyPDF(self):
        """
        Returns different object but copy of PDF.

        Returns
        ---
        PDF
            Copy of self.

        """
        pdf = PDF(self.pageBank)
        pdf._setOrderedPages(self._getOrderedPages().copy())
        return(pdf)


class PDFHistoryRecorder():
    """
    Object that contains a ordered history of versions of a PDf object.
    
    Attributes
    ---
    currentVersion : int
        Current version of PDF that is selected currently by object using PDFHistoryRecorder.
    versions : list <PDF>
        Ordered versions of PDF.

    """
    def __init__(self):
        self.currentVersion = -1   # First pdf starts at 0 index
        self.versions = []

    def _getVersions(self):
        return(self.versions)

    def _getCurrentVersion(self):
        return(self.currentVersion)

    def _setCurrentVersion(self, i):
        self.currentVersion = i

    def newVersion(self, pdf):
        """
        Erase all later versions and add pdf to versions.

        """
        self.currentVersion += 1
        self.versions = self.versions[:self.currentVersion]
        self.versions.append(pdf.copyPDF())

    def previousVersion(self):
        """
        Changes back to previous version and returns a copy of that pdf, if no previous versions raises exception.

        Raises
        ---
        NoPrevVersions
            Thrown if there are no previous versions (i.e. current index less than or equal to 0).

        """
        if self.currentVersion > 0:
            self.currentVersion -= 1
            return(self.versions[self.currentVersion].copyPDF())
        else:
            raise(NoPrevVersions('No previous versions to rollback to.'))

    def laterVersion(self):
        """
        Changes forward to later version and returns a copy of that pdf, if no later version raises exception.

        Raises
        ---
        NoLaterVersions
            Thrown if there are no future versions (i.e. current index greater than or equal to length of versions).

        """
        if self.currentVersion < len(self.versions)-1:
            self.currentVersion += 1
            return(self.versions[self.currentVersion].copyPDF())
        else:
            raise(NoLaterVersions('No later versions to rollforward to.'))

