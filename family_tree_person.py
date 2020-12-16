# family_tree_person.py

class Person(object):
    # This class and its derivatives provide a data-structure independent
    # of any kind of genealogical file format (e.g., GEDCOM.)  By separation
    # of concerns, no file-format-specific code should exist here.

    def __init__(self):
        self.mother = None
        self.father = None
        self.name = ''

class MalePerson(Person):
    def __init__(self):
        self.spouse_list = []

class FemalePerson(Person):
    def __init__(self):
        self.child_list = []