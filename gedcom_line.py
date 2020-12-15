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

        self.pointer = None

    def patch_pointer(self, xref_map):
        if type(self.value) is list and len(self.value) > 0 and type(self.value[0]) is str:
            if self.value[0][0] == '@' and self.value[0][-1] == '@':
                if self.value[0] in xref_map:
                    self.pointer = xref_map[self.value[0]]
                else:
                    raise GedcomException('Failed to patch pointer "%s".' % self.value[0])
        for line in self.sub_line_list:
            line.patch_pointer(xref_map)