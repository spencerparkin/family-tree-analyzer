# search_results.py

from PIL import Image

class SearchResults(object):
    def __init__(self):
        super().__init__()
        self.no_baptism_list = []
        self.no_endownment_list = []
        self.no_sealing_to_parents_list = []
        self.no_sealing_to_spouse_list = []

    def conditionally_accumulate(self, relationship):
        person = relationship.person
        if person.deathday is not None:
            if person.baptism_date is None and not person.died_before_eight:
                self.no_baptism_list.append(relationship)
            if person.endownment_date is None:
                self.no_endownment_list.append(relationship)
            if person.sealing_to_parents_date is None and not person.born_in_the_covenant:
                self.no_sealing_to_parents_list.append(relationship)
            if person.sealing_to_spouse_date is None:
                self.no_sealing_to_spouse_list.append(relationship)

    def generate_text_file(self, out_file):
        raise Exception('Not yet implimented')

    def generate_csv_file(self, out_file):
        raise Exception('Not yet implimented')

    def generate_png_file(self, out_file, root_person):
        person_subset = {root_person}
        person_subset = person_subset.union({person for person in self.no_baptism_list})
        person_subset = person_subset.union({person for person in self.no_endownment_list})
        person_subset = person_subset.union({person for person in self.no_sealing_to_parents_list})
        person_subset = person_subset.union({person for person in self.no_sealing_to_spouse_list})

        print('Generating render tree...')
        visitation_set = set()
        root_node = root_person.generate_render_tree(visitation_set)
        size_before = root_node.calculate_size()

        #print('Pruning render tree...')
        #root_node.prune_tree(person_subset)
        #size_after = root_node.calculate_size()
        #percentage = 100.0 * size_after / size_before
        #print('Tree reduced to %d%% of it\'s former size.' % percentage)

        print('Calculating tree layout...')
        root_node.calculate_graph_layout()
        root_node.calculate_bounding_box()

        print('Rendering tree to image...')
        image = Image.new('RGBA', (1024, 1024), (255, 255, 255, 0))
        root_node.render_graph(image)
        image.save(out_file)