# family_tree_analyzer.py

import os
import argparse
import sys

sys.path.append(r'C:\git_repos\pyMath2D')

from family_tree_data import FamilyTreeData
from family_tree_walker import FamilyTreeWalker
from gedcom_transmission import GedcomTransmission
from search_results import SearchResults

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze family tree data to determine persons needing LDS ordinances by proxy.')
    parser.add_argument('--inFile', dest='in_file', help='Read the given file; typically a GEDCOM file.')
    parser.add_argument('--outFile', dest='out_file', help='Write the given file; this can be a text file or an image file.')
    parser.add_argument('--rootID', dest='root_id', help='Family search ID of person that is the starting-point for a search performed in the family tree.')

    args = parser.parse_args()

    family_tree_data = FamilyTreeData()

    ext = os.path.splitext(args.in_file)[1]
    if ext == '.ged':
        with open(args.in_file, mode='r', encoding='utf-8-sig') as input_stream:
            print('Loading GEDCOM file %s...' % args.in_file)
            transmission = GedcomTransmission()
            transmission.recv(input_stream)
            print('Building family tree data...')
            family_tree_data.from_gedcom_transmission(transmission)
    else:
        raise Exception('Files of extension "%s" are not yet supported.' % ext)

    print('Found %d people in the family tree.' % len(family_tree_data.person_list))

    root_person = None
    if args.root_id is not None:
        key = args.root_id.upper()
        if not key in family_tree_data.family_search_index:
            raise Exception('No person with ID "%s" could be found in the tree.' % key)
        root_person = family_tree_data.family_search_index[key]

    if root_person is None:
        root_person = family_tree_data.person_list[0]

    print('Root person: "%s"' % root_person.name)

    search_results = SearchResults()

    def visitation_func(relationship, search_results):
        if search_results.max_results_reached():
            return False
        search_results.conditionally_accumulate(relationship)
        return True

    print('Searching for deceased relatives needing proxy work...')
    walker = FamilyTreeWalker(root_person)
    walker.visitation_func = visitation_func
    walker.visitation_data = search_results
    walker.walk()

    print('Generating report file "%s"...' % args.out_file)
    ext = os.path.splitext(args.out_file)[1]
    if ext == '.txt':
        search_results.generate_text_file(args.out_file)
    elif ext == '.csv':
        search_results.generate_csv_file(args.out_file)
    elif ext == '.png':
        search_results.generate_png_files(args.out_file, root_person)
    else:
        raise Exception('File extension "%s" not supported.' % ext)