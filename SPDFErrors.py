class NotUniqueError(Exception):
    """
    Thrown when entry is not unique.
    
    """
    pass


class NotInBankError(Exception):
    """
    Thrown when no matching object is found in bank.
    
    """
    pass


class FilePathNotPDF(Exception):
    """
    Thrown when given file path is not a valid .pdf.

    """
    pass