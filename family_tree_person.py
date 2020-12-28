# family_tree_person.py

import requests

from render_tree import RenderNode
from lxml import etree

class Person(object):
    # This class and its derivatives provide a data-structure independent
    # of any kind of genealogical file format (e.g., GEDCOM.)

    def __init__(self):
        super().__init__()
        self.mother = None
        self.father = None
        self.name = ''
        self.birthday = None
        self.deathday = None
        self.christening_date = None
        self.baptism_date = None
        # TODO: Do we need an initiatory date?
        self.endownment_date = None
        self.sealing_to_spouse_date = None
        self.sealing_to_parents_date = None
        self.born_in_the_covenant = None
        self.died_before_eight = None
        self.family_search_id = None

    def generate_render_tree(self, visitation_set):
        visitation_set.add(hex(id(self)))
        render_node = RenderNode(person=self)
        if self.mother and not hex(id(self.mother)) in visitation_set:
            render_node.sub_node_map['mother'] = self.mother.generate_render_tree(visitation_set)
        if self.father and not hex(id(self.father)) in visitation_set:
            render_node.sub_node_map['father'] = self.father.generate_render_tree(visitation_set)
        return render_node

    def post_load_fixup(self):
        pass

    def calc_life_span(self):
        life_span = None
        if self.deathday is not None:
            if self.birthday is not None:
                life_span = self.deathday - self.birthday
            elif self.christening_date is not None:
                life_span = self.deathday - self.christening_date
        return life_span

    def had_any_children(self):
        return False

    def web_scrape(self):
        url = 'https://www.familysearch.org/tree/person/ordinances/%s' % self.family_search_id
        print('Requesting URL: ' + url)
        headers = {'Content-Type': 'text/html'}
        request = requests.get(url, headers=headers)
        html_text = request.text
        print('Parsering HTML...')
        html_parser = etree.HTMLParser()
        html_tree = etree.fromstring(html_text, html_parser)
        print('Analyzing HTML...')
        xpath = '//fs-tree-person-ordinance'
        html_node = html_tree.xpath(xpath)
        # Alas, this will never work.  I was naive to think I could just fetch the page.
        # That won't work, because the page is dynamically generates client-side as well
        # as probably server-side too.  What you might be able to do is open the page
        # in an external browser, and then use Selenium to browse the page procedurally.
        # This is certainly more time-consuming, but it would work.
        html_node = None

class MalePerson(Person):
    def __init__(self):
        super().__init__()
        self.spouse_list = []

    def generate_render_tree(self, visitation_set):
        render_node = super().generate_render_tree(visitation_set)
        i = 1
        for spouse in self.spouse_list:
            if hex(id(spouse)) not in visitation_set:
                render_node.sub_node_map['spouse_%d' % i] = spouse.generate_render_tree(visitation_set)
                i += 1
        return render_node

    def had_any_children(self):
        for spouse in self.spouse_list:
            for child in spouse.child_list:
                if child.father == self:
                    return True
        return False

class FemalePerson(Person):
    def __init__(self):
        super().__init__()
        self.child_list = []

    def generate_render_tree(self, visitation_set):
        render_node = super().generate_render_tree(visitation_set)
        i = 1
        for child in self.child_list:
            if hex(id(child)) not in visitation_set:
                render_node.sub_node_map['child_%d' % i] = child.generate_render_tree(visitation_set)
                i += 1
        return render_node

    def post_load_fixup(self):
        if any([child.mother != self for child in self.child_list]):
            raise Exception('Mother had someone else\'s child.')

    def had_any_children(self):
        return True if len(self.child_list) > 0 else False