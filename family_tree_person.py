# family_tree_person.py

from render_tree import RenderNode

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