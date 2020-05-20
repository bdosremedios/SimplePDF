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


class NoPrevVersions(Exception):
    """
    Thrown when there are no previous versions available.

    """
    pass


class NoLaterVersions(Exception):
    """
    Thrown when there are no later versions available.

    """
    pass


class NoValidFilePathGiven(Exception):
    """
    Thrown when no valid file path was given.

    """
    pass

