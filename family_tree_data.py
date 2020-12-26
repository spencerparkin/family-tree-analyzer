# family_tree_data.py

from gedcom_exception import GedcomException
from family_tree_person import MalePerson, FemalePerson, Person
from datetime import datetime

class FamilyTreeData(object):
    def __init__(self):
        self.person_list = []
        self.family_search_index = {}

    def from_gedcom_transmission(self, transmission):
        # Decypher the given GEDCOM transmission in terms of the Lineage-Linked Grammar.
        # At the time of this writing, not all information is gathered into our internal data-structure.

        if len(transmission.record_list) == 0:
            raise GedcomException('Cannot create family-tree data from vacuous transmission.')

        header = transmission.record_list[0]
        if header.tag != 'HEAD':
            raise GedcomException('Did not find header record.')

        trailer = transmission.record_list[-1]
        if trailer.tag != 'TRLR':
            raise GedcomException('Did not find trailer record.')

        # Go load all the individual records.
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

        # Lastly, do any needed post-load processing.
        for person in self.person_list:
            person.post_load_fixup()

    def to_gedcom_transmission(self):
        raise GedcomException('Not yet implimented.')

    def generate_datetime(self, date_line):
        if date_line is not None:
            date_text = ' '.join(date_line.value)
            date_format_list = [
                '%Y',
                'ABT %Y',
                '%B %Y',
                '%b %Y',
                '%d %B %Y',
                '%d %b %Y'
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
            person = Person()
        elif sex_line.value[0] == 'M':
            person = MalePerson()
        elif sex_line.value[0] == 'F':
            person = FemalePerson()
        else:
            raise GedcomException('SEX field of person was neither "M" nor "F".')

        family_search_id_line = record.find_sub_line('_FSFTID')
        if family_search_id_line is not None:
            person.family_search_id = family_search_id_line.value[0]

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

        christening_line = record.find_sub_line('CHR')
        if christening_line is not None:
            person.christening_date = self.generate_datetime(christening_line.find_sub_line('DATE'))

        life_span = person.calc_life_span()
        if life_span is not None:
            person.died_before_eight = life_span.days < 365 * 8

        # Note that this is not needed if the child died before reaching the age of accountability.
        baptism_line = record.find_sub_line('BAPL')
        if baptism_line is not None:
            person.baptism_date = self.generate_datetime(baptism_line.find_sub_line('DATE'))
            status_line = baptism_line.find_sub_line('STAT')
            if status_line is not None:
                if status_line.value[0] == 'CHILD' or status_line.value[0] == 'STILLBORN':
                    person.died_before_eight = True

        endownment_line = record.find_sub_line('ENDL')
        if endownment_line is not None:
            person.endownment_date = self.generate_datetime(endownment_line.find_sub_line('DATE'))

        # Note that this is not needed if the child is born in the covenant.
        sealing_to_parents_line = record.find_sub_line('SLGC')
        if sealing_to_parents_line is not None:
            person.sealing_to_parents_date = self.generate_datetime(sealing_to_parents_line.find_sub_line('DATE'))
            status_line = sealing_to_parents_line.find_sub_line('STAT')
            if status_line is not None:
                if status_line.value[0] == 'BIC':
                    person.born_in_the_covenant = True

        return person

    def patch_gedcom_person_relationships(self, family_record, person_map):
        husband_record = family_record.find_sub_line('HUSB')
        wife_record = family_record.find_sub_line('WIFE')

        if husband_record is not None:
            husband = person_map[hex(id(husband_record.pointer))]

        if wife_record is not None:
            wife = person_map[hex(id(wife_record.pointer))]

        if husband_record is not None and wife_record is not None:
            husband.spouse_list.append(wife)

        for child_record in family_record.for_all_sub_lines('CHIL'):
            child = person_map[hex(id(child_record.pointer))]
            if wife_record is not None:
                wife.child_list.append(child)
                child.mother = wife
            if husband_record is not None:
                child.father = husband

        sealing_to_spouse_line = family_record.find_sub_line('SLGS')
        if sealing_to_spouse_line is not None:
            sealing_to_spouse_date = self.generate_datetime(sealing_to_spouse_line.find_sub_line('DATE'))
            if sealing_to_spouse_date is not None:
                if husband is not None:
                    husband.sealing_to_spouse_date = sealing_to_spouse_date
                if wife is not None:
                    wife.sealing_to_spouse_date = sealing_to_spouse_date
                    for child in wife.child_list:
                        if child.birthday is not None:
                            child.born_in_the_covenant = True if child.birthday > sealing_to_spouse_date else False