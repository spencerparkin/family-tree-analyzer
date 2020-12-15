# gedcom_transmission.py

from gedcom_exception import GedcomException
from gedcom_line import GedcomLine

class GedcomTransmission(object):
    # Instances of this class can send or receive any kind of GEDCOM transmission.
    # Such transmissions may or may not contain any actual genealogical information
    # as the transmission protocol is independent of such data, although it was designed
    # to lend itself to such data.

    def __init__(self):
        self.record_list = []

    def recv(self, input_stream):
        # Receive a self-contained GEDCOM transmission from the given input stream.

        xref_map = {}   # This is used to link cross-references during reception of the transmission.
        line_stack = None
        line_number = 0
        while input_stream.readable():
            line_number += 1
            line_text = input_stream.readline()
            if len(line_text) == 0:
                break
            try:
                line = GedcomLine(line_text)
                if line.level == 0:
                    if line_stack is not None and len(line_stack) > 0:
                        self.record_list.append(line_stack[0])
                    line_stack = [line]
                else:
                    parent = line_stack[line.level - 1]
                    parent.sub_line_list.append(line)
                    while len(line_stack) > line.level:
                        line_stack.pop()
                    line_stack.append(line)
                if line.xref_id is not None:
                    xref_map[line.xref_id] = line
            except Exception as ex:
                raise GedcomException('Failed to parse line %d.' % line_number) from ex
        if line_stack is not None and len(line_stack) > 0:
            self.record_list.append(line_stack[0])
        for line in self.record_list:
            line.patch_pointer(xref_map)

    def send(self, output_stream):
        pass