"""
TemplateParser can parse .lfm, .itm, .fct, .rm
"""
class TemplateParser(object):
    def __init__(self, templatefile=None):
        self.templatefile = templatefile
        self.data = {'filename': templatefile}
        if templatefile:
            self._initialize()

    @property
    def class_type(self):
        try:
            class_type = self.data['settings']['class_type']
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
        sections = [line.replace('***', '').lstrip().rstrip().lower() for line in unspaced if '***' in line]
        indices = [i for i, line in enumerate(unspaced) if '***' in line]
        for i, number in enumerate(indices):
            if i + 1 == len(indices):
                base_dict[sections[i]] = self.key_values(unspaced[number + 1:])
            else:
                base_dict[sections[i]] = self.key_values(unspaced[number + 1:indices[i + 1]])
        return base_dict

    def _initialize(self):
        self.data = self.template_lines_to_dict(self.list_lines_from_template(self.templatefile))

    def load_data(self, templatefile):
        """
        Return list of dictionaries with all template data
        :param templatefile:
        :return: list of dictionaries of template sections
        """
        self.data = self.template_lines_to_dict(self.list_lines_from_template(templatefile))
        return self.data

    def key_values(self, lines):
        key_values = {}
        line_list = []
        for i, line in enumerate(lines):
            try:
                key_values.update(self._parse_key_values(line))
            except ValueError:
                line_list.append(line)
        if line_list:
            return line_list
        else:
            return key_values

    def _parse_key_values(self, line):
        """
        Lines in a template can be in 3 formats:

        <item:value> --> in this case a dictionary like {'item': 'value'} will be returned
        <item value value value ...> --> in this case a dictionary like {'item': [value, value, value]}
        <a_single_item_with_no_spaces> --> lines like this should never reach this method

        :param line: a single line from a template file
        :return: see above
        """
        # Return first element of split line, and list of all other values
        if ':' not in line:
            if len(line.split()) > 1:
                return {line.split()[0]: line.split()[1:]}
            else:
                return line

        # Get key and values from line, convert values to True/False/None/Int if needed
        split_line = [item.strip() for item in line.split(':')]
        key, values = split_line[0], [item.strip() for item in split_line[1].split()]
        values = [self.string_literal(value) for value in values]

        # Return either {key: value} or {key: ['list', 'of', 'values']}
        if len(values) == 1:
            return {key: values[0]}
        else:
            return {key: values}

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
    import pprint
    a = TemplateParser()
    print(' TEST 1 : Lifeform ')
    pprint.pprint(a.load_data('gameobjects/lifeform/zaxim.lfm'))
    print(' TEST 2 : Item ')
    pprint.pprint(a.load_data('gameobjects/weapon/long_sword.itm'))
    print(' TEST 3 : Room ')
    pprint.pprint(a.load_data('gameobjects/room/template.rm'))
    print(' TEST 4 : Faction ')
    pprint.pprint(a.load_data('gameobjects/faction/chand_baori.fct'))


