# family_tree_analyzer.py

import os
import argparse

from family_tree_data import FamilyTreeData
from family_tree_walker import FamilyTreeWalker
from gedcom_transmission import GedcomTransmission

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze family tree data.')
    parser.add_argument('--inFile', dest='in_file', help='Read the given file; typically a GEDCOM file.')
    parser.add_argument('--rootID', dest='root_id', help='Family search ID of person that is the starting-point for a search performed in the family tree.')
    parser.add_argument('--findUndoneBaptisms', dest='find_undone_baptisms', help='Find people who have no baptismal date listed.', action='store_true')

    args = parser.parse_args()

    family_tree_data = FamilyTreeData()

    ext = os.path.splitext(args.in_file)[1]
    if ext == '.ged':
        with open(args.in_file, mode='r', encoding='utf-8-sig') as input_stream:
            transmission = GedcomTransmission()
            transmission.recv(input_stream)
            family_tree_data.from_gedcom_transmission(transmission)
    else:
        raise Exception('Files of extension "%s" are not yet supported.' % ext)

    print('Found %d people in family tree.' % len(family_tree_data.person_list))

    root_person = None
    if args.root_id is not None:
        key = args.root_id.upper()
        if not key in family_tree_data.family_search_index:
            raise Exception('No person with ID "%s" could be found in the tree.' % key)
        root_person = family_tree_data.family_search_index[key]

    if args.find_undone_baptisms:
        if root_person is None:
            raise Exception('No root person given for search.')
        # I'm not sure how to just pass the count variable by reference as part of the closure.
        visitation_data = {'count': 0}
        def visitation_func(relationship, visitation_data):
            person = relationship.person
            if person.baptism_date is None and person.deathday is not None:
                print('-------------------------------')
                print('Name: ' + person.name)
                print('ID: ' + str(person.family_search_id))
                print('Relationship: ' + str(relationship))
                visitation_data['count'] += 1

        print('Deceased persons in your tree who do not have a baptismal date listed...')
        walker = FamilyTreeWalker(root_person)
        walker.visitation_func = visitation_func
        walker.visitation_data = visitation_data
        walker.walk()
        print('-------------------------------')
        print('Found %d persons.' % visitation_data['count'])