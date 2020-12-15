# family_tree_data.py

from gedcom_exception import GedcomException

class FamilyTreeData(object):
    def __init__(self):
        pass

    def from_gedcom_transmission(self, transmission):
        # Decypher the given GEDCOM transmission in terms of the Lineage-Linked Grammmar.

        pass

    def to_gedcom_transmission(self):
        raise GedcomException('Not yet implimented.')