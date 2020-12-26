# family_tree_person.py

from render_tree import RenderNode

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