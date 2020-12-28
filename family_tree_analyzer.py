# family_tree_analyzer.py

import os
import argparse
import sys
import json

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
    parser.add_argument('--maxResults', dest='max_search_results', help='Maximum number of people to show per result tree.')
    parser.add_argument('--avoidInlaws', dest='avoid_inlaws', help='Avoid searching up through ancestors of in-laws.', action='store_true')
    parser.add_argument('--avoidSpouses', dest='avoid_spouses', help='Avoid searching spouses (and therefore also children) of any ancestor.', action='store_true')
    parser.add_argument('--webScrape', dest='web_scrape', help='Rather than generate a report, scrape search results from FamilySearch.org for additional information which can be used in subsequent invocations.', action='store_true')
    parser.add_argument('--username', dest='username', help='Provide FamilySearch.org username for scraping.')
    parser.add_argument('--password', dest='password', help='Provide FamilySearch.org password for scraping.')

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

    scrape_cache = {}
    scrape_cache_file = os.path.join(os.getcwd(), 'scrape_cache.json')
    if os.path.exists(scrape_cache_file):
        with open(scrape_cache_file, 'r') as handle:
            json_text = handle.read()
            scrape_cache = json.loads(json_text)

    for person in family_tree_data.person_list:
        person.consume_scrape_cache(scrape_cache)

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
    if args.max_search_results is not None:
        search_results.max_results = int(args.max_search_results)

    def visitation_func(relationship, search_results):
        if search_results.max_results_reached():
            return False
        search_results.conditionally_accumulate(relationship)
        return True

    print('Searching for deceased relatives needing proxy work...')
    walker = FamilyTreeWalker(root_person)
    walker.visitation_func = visitation_func
    walker.visitation_data = search_results
    walker.avoid_inlaws = args.avoid_inlaws
    walker.avoid_spouses = args.avoid_spouses
    walker.walk()

    if args.web_scrape:
        print('Web scraping search results...')

        # Add directory to path where web-driver executables can be found for Selenium.
        # These are servers that act as the intermediary/abstraction-layer between our
        # script (which uses the selenium API) and the actual browser.
        web_drivers_dir = os.path.join(os.getcwd(), 'web_drivers')
        path = os.environ['PATH']
        path_list = path.split(';')
        path_list.append(web_drivers_dir)
        path = ';'.join(path_list)
        os.environ['PATH'] = path

        from selenium import webdriver
        driver = webdriver.Chrome()

        driver.get('https://www.familysearch.org/en/')
        element = driver.find_element_by_xpath('//*[@id="signInLink"]')
        element.click()

        element = driver.find_element_by_xpath('//*[@id="userName"]')
        element.send_keys(args.username)

        element = driver.find_element_by_xpath('//*[@id="password"]')
        element.send_keys(args.password)

        element = driver.find_element_by_xpath('//*[@id="login"]')
        element.click()

        search_results.web_scrape(driver, scrape_cache)
        driver.close()

        with open(scrape_cache_file, 'w') as handle:
            json_text = json.dumps(scrape_cache, indent=4)
            handle.write(json_text)

        print('Wrote scrape cache to file: ' + scrape_cache_file)
    else:
        print('Generating report file "%s"...' % args.out_file)
        ext = os.path.splitext(args.out_file)[1]
        if ext == '.txt':
            search_results.generate_text_file(args.out_file)
        elif ext == '.csv':
            search_results.generate_csv_file(args.out_file)
        elif ext == '.png':
            search_results.generate_png_files(args.out_file, root_person, True)
        else:
            raise Exception('File extension "%s" not supported.' % ext)