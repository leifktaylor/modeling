TEMPLATE_FILE = 'gameobjects/faction/chand_baori.fct'


class TemplateParser(object):
    def __init__(self, templatefile):
        self.data = {'filename': templatefile}
        self.initialize()

    @property
    def class_type(self):
        try:
            class_type = self.data['settings']['gameobject']
        except KeyError:
            class_type = 'GameObject'
        return class_type

    @property
    def sections(self):
        return [key for key in self.data.keys() if key != 'filename']

    @property
    def filename(self):
        return self.data['filename']

    def template_lines_to_dict(self, line_list):
        # Get rid of all comments in all lines
        uncommented = [line.split('#', 1)[0].rstrip() for line in line_list]
        # Get rid of empty lines
        unspaced = [line for line in uncommented if line]
        # divide into sections (section markers in .rm file are '*** section_name ***')
        base_dict = {}
        sections = [line.replace('***', '').lstrip().rstrip() for line in unspaced if '***' in line]
        indices = [i for i, line in enumerate(unspaced) if '***' in line]
        for i, number in enumerate(indices):
            if i + 1 == len(indices):
                base_dict[sections[i]] = self.key_values(unspaced[number + 1:])
            else:
                base_dict[sections[i]] = self.key_values(unspaced[number + 1:indices[i + 1]])
        return base_dict

    def initialize(self):
        new_data = self.template_lines_to_dict(self.list_lines_from_template(self.data['filename']))
        self.data.update(new_data)

    def key_values(self, lines):
        key_values = {}
        for line in lines:
            key_values.update(self._parse_key_values(line))
        return key_values

    def _parse_key_values(self, line):
        try:
            key, value = line.split(':')[0], self.string_literal(line.split(':')[1])
            return {key: value}
        except IndexError:
            return {line: None}

    @staticmethod
    def list_lines_from_template(filename):
        with open(filename, 'r') as template_file:
            return [line.strip('\n') for line in template_file.readlines()]

    @staticmethod
    def string_literal(string):
        if string.lower() in ['yes', 'true', 'y']:
            return True
        elif string.lower() in ['no', 'false', 'n']:
            return False
        elif string == ['None']:
            return None
        elif string.isdigit():
            return int(string)
        else:
            return string


if __name__ == '__main__':
    a = TemplateParser(TEMPLATE_FILE)
    a.initialize()
    import pprint
    print('Class Type: . . {0}'.format(a.class_type))
    print('Sections: . . . {0}'.format(a.sections))
    pprint.pprint(a.data)


