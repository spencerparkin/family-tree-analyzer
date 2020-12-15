# gedcom_exception.py

class GedcomException(Exception):
    def __init__(self, error):
        super().__init__(error)