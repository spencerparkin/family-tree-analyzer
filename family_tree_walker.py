# family_tree_walker.py

from family_tree_person import MalePerson, FemalePerson

class Relationship(object):
    def __init__(self, person, path):
        self.person = person
        self.path = path

    def __str__(self):
        if len(self.path) == 0:
            return 'you'
        # TODO: Reduce path when possible.  E.g., your father's spouse's son becomes your brother.
        return 'your ' + ' '.join([part + '\'s' for part in self.path[:-1]] + [self.path[-1]])

class FamilyTreeWalker(object):
    def __init__(self, root_person):
        self.root_person = root_person
        self.visitation_func = None
        self.visitation_data = None
        self.max_relationship_path_length = -1
        self.avoid_inlaws = True

    def walk(self):
        visitation_set = set()
        relationship = Relationship(self.root_person, [])
        queue = [relationship]
        while len(queue) > 0:
            relationship = queue.pop()
            self.visit(relationship)
            person = relationship.person
            visitation_set.add(person)
            if self.max_relationship_path_length == -1 or len(relationship.path) < self.max_relationship_path_length:
                if not self.avoid_inlaws or 'spouse' not in relationship.path:
                    if person.mother is not None and person.mother not in visitation_set:
                        queue.append(Relationship(person.mother, relationship.path + ['mother']))
                    if person.father is not None and person.father not in visitation_set:
                        queue.append(Relationship(person.father, relationship.path + ['father']))
                if hasattr(person, 'spouse_list'):
                    for spouse in person.spouse_list:
                        if spouse not in visitation_set:
                            queue.append(Relationship(spouse, relationship.path + ['spouse']))
                if hasattr(person, 'child_list'):
                    for child in person.child_list:
                        if child not in visitation_set:
                            if isinstance(child, MalePerson):
                                queue.append(Relationship(child, relationship.path + ['son']))
                            elif isinstance(child, FemalePerson):
                                queue.append(Relationship(child, relationship.path + ['daughter']))

    def visit(self, relationship):
        if self.visitation_func is not None:
            self.visitation_func(relationship, self.visitation_data)