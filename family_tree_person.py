# family_tree_person.py

class Person(object):
    # This class and its derivatives provide a data-structure independent
    # of any kind of genealogical file format (e.g., GEDCOM.)  By separation
    # of concerns, no file-format-specific code should exist here.

    def __init__(self):
        super().__init__()
        self.mother = None
        self.father = None
        self.name = ''
        self.birthday = None
        self.deathday = None
        self.baptism_date = None
        self.endownment_date = None
        self.sealing_to_spouse_date = None
        self.sealing_to_parents_date = None
        self.born_in_the_covenant = None
        self.family_search_id = None

class MalePerson(Person):
    def __init__(self):
        super().__init__()
        self.spouse_list = []

class FemalePerson(Person):
    def __init__(self):
        super().__init__()
        self.child_list = []