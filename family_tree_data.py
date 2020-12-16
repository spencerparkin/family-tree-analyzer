# family_tree_data.py

from gedcom_exception import GedcomException
from family_tree_person import MalePerson, FemalePerson
from datetime import datetime

class FamilyTreeData(object):
    def __init__(self):
        self.person_list = []
        self.family_search_index = {}

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

        # Build an index by family search's family tree ID.
        self.family_search_index = {}
        for person in self.person_list:
            if person.family_search_id is not None:
                self.family_search_index[person.family_search_id] = person

    def to_gedcom_transmission(self):
        raise GedcomException('Not yet implimented.')

    def generate_datetime(self, date_line):
        if date_line is not None:
            date_text = ' '.join(date_line.value)
            date_format_list = [
                '%d %b %Y',
                '%Y'
            ]
            for date_format in date_format_list:
                try:
                    date_obj = datetime.strptime(date_text, date_format)
                    return date_obj
                except ValueError as ve:
                    pass
        return None

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

        birth_line = record.find_sub_line('BIRT')
        if birth_line is not None:
            person.birthday = self.generate_datetime(birth_line.find_sub_line('DATE'))

        death_line = record.find_sub_line('DEAT')
        if death_line is not None:
            person.deathday = self.generate_datetime(death_line.find_sub_line('DATE'))

        # Note that this is not needed if the child was a stillborn.
        baptism_line = record.find_sub_line('BAPL')
        if baptism_line is not None:
            person.baptism_date = self.generate_datetime(baptism_line.find_sub_line('DATE'))

        endownment_line = record.find_sub_line('ENDL')
        if endownment_line is not None:
            person.endownment_date = self.generate_datetime(endownment_line.find_sub_line('DATE'))

        sealing_to_spouse_line = record.find_sub_line('SLGS')
        if sealing_to_spouse_line is not None:
            person.sealing_to_spouse_date = self.generate_datetime(sealing_to_spouse_line.find_sub_line('DATE'))

        # Note that this is not needed if the child is born in the covenant.
        sealing_to_parents_line = record.find_sub_line('SLGC')
        if sealing_to_parents_line is not None:
            person.sealing_to_parents_date = self.generate_datetime(sealing_to_parents_line.find_sub_line('DATE'))

        family_search_id_line = record.find_sub_line('_FSFTID')
        if family_search_id_line is not None:
            person.family_search_id = family_search_id_line.value[0]

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
