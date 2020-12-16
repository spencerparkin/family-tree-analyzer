# family_tree_data.py

from gedcom_exception import GedcomException
from family_tree_person import MalePerson, FemalePerson

class FamilyTreeData(object):
    def __init__(self):
        self.person_list = []

    def from_gedcom_transmission(self, transmission):
        # Decypher the given GEDCOM transmission in terms of the Lineage-Linked Grammmar.
        # At the time of this writing, not all information is gathered into our internal data-structure.

        if len(transmission.record_list) == 0:
            raise GedcomException('Cannot create family-tree data from vacuous transmission.')

        header = transmission.record_list[0]
        if header.tag != 'HEAD':
            raise GedcomException('Did not find header record.')

        trailer = transmission.record_list[-1]
        if trailer.tag != 'TRLR':
            raise GedcomException('Did not find trailer record.')

        person_map = {}
        for record in transmission.record_list:
            if record.tag == 'INDI':
                person = self.generate_gedcom_person(record)
                person_map[hex(id(record))] = person

        # Now that all persons are accounted for, make another pass to bind them into family relationships.
        for record in transmission.record_list:
            if record.tag == 'FAM':
                self.patch_gedcom_person_relationships(record, person_map)

        self.person_list = [person_map[key] for key in person_map]

    def to_gedcom_transmission(self):
        raise GedcomException('Not yet implimented.')

    def generate_gedcom_person(self, record):
        sex_line = record.find_sub_line('SEX')
        if sex_line is None:
            raise GedcomException('Failed to find SEX field in person record.')

        if sex_line.value[0] == 'M':
            person = MalePerson()
        elif sex_line.value[0] == 'F':
            person = FemalePerson()
        else:
            raise GedcomException('SEX field of person was neither "M" nor "F".')

        name_line = record.find_sub_line('NAME')
        if name_line is None:
            raise GedcomException('Failed to find NAME field in person record.')

        person.name = ' '.join(name_line.value).replace('/', '')

        return person

    def patch_gedcom_person_relationships(self, family_record, person_map):
        husband_record = family_record.find_sub_line('HUSB')
        if husband_record is None:
            raise GedcomException('Failed to find HUSB field in family record.')

        wife_record = family_record.find_sub_line('WIFE')
        if wife_record is None:
            raise GedcomException('Failed to find WIFE field in family record.')

        husband = person_map[hex(id(husband_record.pointer))]
        wife = person_map[hex(id(wife_record.pointer))]

        husband.spouse_list.append(wife)

        for child_record in family_record.for_all_sub_lines('CHIL'):
            child = person_map[hex(id(child_record.pointer))]
            wife.child_list.append(child)
            child.mother = wife
            child.father = husband
