# gedcom_line.py

from gedcom_exception import GedcomException

class GedcomLine(object):
    def __init__(self, line_text):
        self.sub_line_list = []

        token_list = line_text.split()

        if len(token_list) > 0:
            self.level = int(token_list[0])
        else:
            self.level = None

        if len(token_list) > 1 and token_list[1][0] == '@' and token_list[1][-1] == '@':
            self.xref_id = token_list[1]
            i = 2
        else:
            self.xref_id = None
            i = 1

        if len(token_list) > i:
            self.tag = token_list[i]
        else:
            self.tag = None

        if len(token_list) > i + 1:
            self.value = token_list[i + 1:]
        else:
            self.value = None

        # It's tempting to remove this member and just use the self.value member,
        # but we need a way to preserve the pointer when generating meta-data.
        self.pointer = None

    def patch_pointer(self, xref_map):
        # Use the given map to patch cross-references made from one GEDCOM line to another.
        if type(self.value) is list and len(self.value) > 0 and type(self.value[0]) is str:
            if self.value[0][0] == '@' and self.value[0][-1] == '@':
                if self.value[0] in xref_map:
                    self.pointer = xref_map[self.value[0]]
                else:
                    raise GedcomException('Failed to patch pointer "%s".' % self.value[0])
        for line in self.sub_line_list:
            line.patch_pointer(xref_map)

    def delete_metadata(self):
        # Here we remove any meta-data that was only used during the sending or receiving process.
        # What remains is just the data that constitutes the substance of the GEDCOM transmission.
        if hasattr(self, 'level'):
            del self.level
        if hasattr(self, 'xref_id'):
            del self.xref_id
        if self.pointer is not None:
            self.value = []
        for line in self.sub_line_list:
            line.delete_metadata()

    def generate_metadata(self, metadata_map):
        if self.pointer is not None:
            if not hasattr(self.pointer, 'xref_id'):
                setattr(self.pointer, 'xref_id', '@ref%d@' % metadata_map['next_id'])
                metadata_map['next_id'] += 1
            self.value = [self.pointer.xref_id]

    def print(self, output_stream, level):
        if hasattr(self, 'xref_id') and self.xref_id is not None:
            line_text = '%d %s %s %s' % (level, self.xref_id, self.tag, ' '.join(self.value))
        else:
            line_text = '%d %s %s' % (level, self.tag, ' '.join(self.value))
        output_stream.write(line_text)
        for line in self.sub_line_list:
            self.print(output_stream, level + 1)

    def find_sub_line(self, tag_name):
        if self.tag == tag_name:
            return self
        for line in self.sub_line_list:
            found_line = line.find_sub_line(tag_name)
            if found_line is not None:
                return found_line

    def find_all_sub_lines(self, tag_name, line_list):
        if self.tag == tag_name:
            line_list.append(self)
        for line in self.sub_line_list:
            self.find_all_sub_lines(tag_name, line_list)

    def for_all_sub_lines(self, tag_name):
        if self.tag == tag_name:
            yield self
        for line in self.sub_line_list:
            yield from line.for_all_sub_lines(tag_name)