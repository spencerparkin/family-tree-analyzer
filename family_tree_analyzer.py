# family_tree_analyzer.py

import os
import argparse

from family_tree_data import FamilyTreeData
from gedcom_transmission import GedcomTransmission

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze family tree data.')
    parser.add_argument('--infile', dest='in_file', help='Read the given file; typically a GEDCOM file.')

    args = parser.parse_args()

    family_tree_data = FamilyTreeData()

    with open(args.in_file, mode='r', encoding='utf-8-sig') as input_stream:
        ext = os.path.splitext(args.in_file)[1]
        if ext == '.ged':
            transmission = GedcomTransmission()
            transmission.recv(input_stream)
            family_tree_data.from_gedcom_transmission(transmission)
        else:
            raise Exception('Files of extension "%s" not supported.' % ext)

    # TODO: Analyze family_tree_data as requested.