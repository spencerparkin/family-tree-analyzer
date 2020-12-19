# render_tree.py

from math2d_vector import Vector
from math2d_aa_rect import AxisAlignedRectangle
from math2d_affine_transform import AffineTransform

class RenderNode(object):
    def __init__(self, person):
        super().__init__()
        self.person = person
        self.sub_node_map = {}
        self.label_string = person.name + '\n' + person.family_search_id
        self.label_box = AxisAlignedRectangle()
        self.bounding_box = None

    def calculate_size(self):
        size = 0
        for node in self.all_nodes():
            size += 1
        return size

    def render_graph(self, draw, image, font):
        image_rect = AxisAlignedRectangle(Vector(0.0, 0.0), Vector(float(image.width), float(image.height)))
        world_rect = self.bounding_box.Copy()
        world_rect.ExpandToMatchAspectRatioOf(image_rect)
        for node in self.all_nodes():
            node.render_edges(draw, font, image_rect, world_rect)
        for node in self.all_nodes():
            node.render_label_box(draw, font, image_rect, world_rect)

    def render_edges(self, draw, font, image_rect, world_rect):
        point_a = world_rect.Map(self.label_box.Center(), image_rect)
        for key in self.sub_node_map:
            sub_node = self.sub_node_map[key]
            point_b = world_rect.Map(sub_node.label_box.Center(), image_rect)
            draw.line((point_a.x, point_a.y, point_b.x, point_b.y), fill=(50, 100, 100), width=1)
            point_c = (point_a + point_b) * 0.5
            text_size = draw.textsize(text=key, font=font)
            draw.text((point_c.x - text_size[0] / 2, point_c.y - text_size[1] / 2), text=key, font=font, fill=(0, 0, 0))

    def render_label_box(self, draw, font, image_rect, world_rect):
        point_a = world_rect.Map(self.label_box.min_point, image_rect)
        point_b = world_rect.Map(self.label_box.max_point, image_rect)
        draw.rectangle((point_a.x, point_a.y, point_b.x, point_b.y), fill=(32, 32, 32))
        polygon = self.label_box.GeneratePolygon()
        for world_line in polygon.GenerateLineSegments():
            image_line = world_rect.Map(world_line, image_rect)
            draw.line((image_line.point_a.x, image_line.point_a.y, image_line.point_b.x, image_line.point_b.y), fill=(255, 0, 0), width=1)
            point = world_rect.Map(self.label_box.Center(), image_rect)
        text_size = draw.textsize(text=self.label_string, font=font)
        draw.text((point.x - text_size[0] / 2, point.y - text_size[1] / 2), text=self.label_string, font=font, fill=(200, 200, 200))

    def transform_graph_layout(self, transform):
        for node in self.all_nodes():
            node.label_box = transform.Transform(node.label_box)
            node.bounding_box = transform.Transform(node.bounding_box)

    def calculate_graph_layout(self, draw, font):
        text_size = draw.textsize(text=self.label_string, font=font)
        text_width = text_size[0]
        text_height = text_size[1]

        total_width = 0.0
        margin = 2.0
        for key in self.sub_node_map:
            sub_node = self.sub_node_map[key]
            sub_node.calculate_graph_layout(draw, font)
            sub_node.calculate_bounding_box()
            total_width += sub_node.bounding_box.Width() + 2.0 * margin

        location = Vector(-total_width / 2.0 + margin, -2.0 * text_height)
        for key in self.sub_node_map:
            sub_node = self.sub_node_map[key]
            transform = AffineTransform()
            upper_left_corner = Vector(sub_node.bounding_box.min_point.x, sub_node.bounding_box.max_point.y)
            transform.Translation(location - upper_left_corner)
            sub_node.transform_graph_layout(transform)
            location.x += sub_node.bounding_box.Width() + 2.0 * margin

        self.label_box.min_point = Vector(-text_width / 2.0 - 3.0, -text_height / 2.0 - 3.0)
        self.label_box.max_point = Vector(text_width / 2.0 + 3.0, text_height / 2.0 + 3.0)

    def calculate_bounding_box(self):
        self.bounding_box = self.label_box.Copy()
        for node in self.all_nodes():
            self.bounding_box.GrowFor(node.label_box)

    def all_nodes(self):
        queue = [self]
        while len(queue) > 0:
            node = queue.pop()
            yield node
            for key in node.sub_node_map:
                sub_node = node.sub_node_map[key]
                queue.append(sub_node)

    def prune_tree(self, person_set):
        del_key_list = []
        for key in self.sub_node_map:
            sub_node = self.sub_node_map[key]
            if not sub_node.any_person_found_in(person_set):
                del_key_list.append(key)
        for key in del_key_list:
            del self.sub_node_map[key]
        for key in self.sub_node_map:
            sub_node = self.sub_node_map[key]
            sub_node.prune_tree(person_set)

    def any_person_found_in(self, person_set):
        for node in self.all_nodes():
            if node.person in person_set:
                return True