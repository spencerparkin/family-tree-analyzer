# search_results.py

import os

from PIL import Image, ImageDraw, ImageFont

class SearchGroup(object):
    def __init__(self):
        super().__init__()
        self.relationship_list = []

    def is_match(self, relationship):
        raise Exception('Pure virtual call.')

class BaptismNeededGroup(SearchGroup):
    def __init__(self):
        super().__init__()

    def is_match(self, relationship):
        person = relationship.person
        return person.baptism_date is None and not person.died_before_eight

class EndownmentNeededGroup(SearchGroup):
    def __init__(self):
        super().__init__()

    def is_match(self, relationship):
        person = relationship.person
        return person.endownment_date is None

class SealingToParentsNeededGroup(SearchGroup):
    def __init__(self):
        super().__init__()

    def is_match(self, relationship):
        person = relationship.person
        return person.sealing_to_parents_date is None and not person.born_in_the_covenant

class SealingToSpouseNeededGroup(SearchGroup):
    def __init__(self):
        super().__init__()

    def is_match(self, relationship):
        person = relationship.person
        return person.sealing_to_spouse_date is None

class SearchResults(object):
    def __init__(self):
        super().__init__()
        self.search_group_list = [
            BaptismNeededGroup(),
            EndownmentNeededGroup(),
            SealingToParentsNeededGroup(),
            SealingToSpouseNeededGroup()
        ]
        self.max_results = 15

    def max_results_reached(self):
        return all([len(search_group.relationship_list) >= self.max_results for search_group in self.search_group_list])

    def conditionally_accumulate(self, relationship):
        if relationship.person.deathday is not None:
            for search_group in self.search_group_list:
                if search_group.is_match(relationship) and len(search_group.relationship_list) < self.max_results:
                    search_group.relationship_list.append(relationship)

    def generate_text_file(self, out_file):
        raise Exception('Not yet implimented')

    def generate_csv_file(self, out_file):
        raise Exception('Not yet implimented')

    def generate_png_files(self, out_file, root_person):
        font = ImageFont.truetype('JetBrainsFonts/static/JetBrainsMono-Regular.ttf')

        # BEGIND EBUG
        #image = Image.new('RGBA', (2048, 2048), (255, 255, 255, 0))
        #draw = ImageDraw.Draw(image)
        #visitation_set = set()
        #root_node = root_person.generate_render_tree(visitation_set)
        #root_node.calculate_graph_layout(draw, font)
        #root_node.calculate_bounding_box()
        #root_node.render_graph(draw, image, font)
        #image.save(out_file)
        #return
        # END DEBUG

        for search_group in self.search_group_list:
            path, ext = os.path.splitext(out_file)
            image_file_path = path + '_' + search_group.__class__.__name__ + ext

            image = Image.new('RGBA', (2048, 2048), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)

            person_subset = {root_person}
            person_subset = person_subset.union({relationship.person for relationship in search_group.relationship_list})

            print('Generating render tree...')
            visitation_set = set()
            root_node = root_person.generate_render_tree(visitation_set)
            size_before = root_node.calculate_size()

            print('Pruning render tree...')
            root_node.prune_tree(person_subset)
            size_after = root_node.calculate_size()
            percentage = 100.0 * size_after / size_before
            print('Tree reduced to %2.2f%% of it\'s former size.' % percentage)

            # TODO: Branches can still be shortened in several ways.

            print('Calculating tree layout...')
            root_node.calculate_graph_layout(draw, font)
            root_node.calculate_bounding_box()

            print('Rendering tree to image file "%s"...' % image_file_path)
            root_node.render_graph(draw, image, font, person_subset)
            image.save(image_file_path)