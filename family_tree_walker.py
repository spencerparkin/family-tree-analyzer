# family_tree_walker.py

from family_tree_person import MalePerson, FemalePerson

class Relationship(object):
    def __init__(self, person, path):
        self.person = person
        self.path = path

    def __str__(self):
        # TODO: Convert path into human-readable sentence.
        return ''

    def spouse_in_path(self):
        return any(['spouse' == component[0] for component in self.path])

class FamilyTreeWalker(object):
    def __init__(self, root_person):
        self.root_person = root_person
        self.visitation_func = None
        self.visitation_data = None
        self.max_relationship_path_length = -1
        self.avoid_inlaws = True
        self.avoid_spouses = False

    def walk(self):
        visitation_set = set()
        relationship = Relationship(self.root_person, [])
        queue = [relationship]
        while len(queue) > 0:
            relationship = queue.pop()
            keep_going = self.visit(relationship)
            if not keep_going:
                break
            person = relationship.person
            visitation_set.add(person)
            if self.max_relationship_path_length == -1 or len(relationship.path) < self.max_relationship_path_length:
                if not self.avoid_inlaws or not relationship.spouse_in_path():
                    if person.mother is not None and person.mother not in visitation_set:
                        queue.append(Relationship(person.mother, relationship.path + [('mother', -1)]))
                    if person.father is not None and person.father not in visitation_set:
                        queue.append(Relationship(person.father, relationship.path + [('father', -1)]))
                if hasattr(person, 'spouse_list') and not self.avoid_spouses:
                    for i, spouse in enumerate(person.spouse_list):
                        if spouse not in visitation_set:
                            queue.append(Relationship(spouse, relationship.path + [('spouse', i)]))
                if hasattr(person, 'child_list'):
                    for i, child in enumerate(person.child_list):
                        if child not in visitation_set:
                            queue.append(Relationship(child, relationship.path + [('child', i)]))

    def visit(self, relationship):
        if self.visitation_func is not None:
            return self.visitation_func(relationship, self.visitation_data)