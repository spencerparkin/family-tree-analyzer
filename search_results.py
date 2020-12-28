# search_results.py

import os

from PIL import Image, ImageDraw, ImageFont
from render_tree import RenderNode

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

        # Try to weed out cases where the individual most likely was
        # not sealed to a spouse because they just died too young.
        if not person.had_any_children():
            life_span = person.calc_life_span()
            if life_span is not None and life_span.days < 365 * 13:
                return False

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

    def web_scrape(self):
        all_people = set()
        for search_group in self.search_group_list:
            all_people = all_people.union({relationship.person for relationship in search_group.relationship_list})
        total_people = len(all_people)
        print('Total people in search results: %d' % total_people)
        i = 0
        for person in all_people:
            i += 1
            print('(%d/%d) Scraping additional info for: %s' % (i, total_people, person.name))
            person.web_scrape()

    def generate_text_file(self, out_file):
        raise Exception('Not yet implimented')

    def generate_csv_file(self, out_file):
        raise Exception('Not yet implimented')

    def generate_png_files(self, out_file, root_person, use_optimal_paths):
        font = ImageFont.truetype('JetBrainsFonts/static/JetBrainsMono-Regular.ttf')

        for search_group in self.search_group_list:
            path, ext = os.path.splitext(out_file)
            image_file_path = path + '_' + search_group.__class__.__name__ + ext

            image = Image.new('RGBA', (4096, 4096), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)

            print('Generating render tree...')

            person_subset = {root_person}
            person_subset = person_subset.union({relationship.person for relationship in search_group.relationship_list})

            if use_optimal_paths:
                # The relationship paths should be of optimal (minimal) length, because
                # they were built using a breadth-first search of the family tree.
                # This is an additive method.
                root_node = RenderNode(person=root_person)
                for relationship in search_group.relationship_list:
                    root_node.construct_using_path(relationship.path)
                size = root_node.calculate_size()
                print('Render tree size: %d' % size)
            else:
                # This is one way to generate the render tree, but it does not necessarily result
                # in optimal paths.  I'm keeping it around, because it is interesting (and perhaps
                # unsettling) to see how I can be related to people on both my mother and father's
                # side of the family tree.  This is a subtractive method.
                visitation_set = set()
                root_node = root_person.generate_render_tree(visitation_set)
                size_before = root_node.calculate_size()
                print('Pruning render tree...')
                root_node.prune_tree(person_subset)
                size_after = root_node.calculate_size()
                percentage = 100.0 * size_after / size_before
                print('Tree reduced to %2.2f%% of its former size.' % percentage)

            print('Calculating tree layout...')
            root_node.calculate_graph_layout(draw, font)
            root_node.calculate_bounding_box()

            print('Rendering tree to image file "%s"...' % image_file_path)
            root_node.render_graph(draw, image, font, person_subset)
            image.save(image_file_path)