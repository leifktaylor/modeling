
class AIParser(object):
    """ parses ai template into ai data structure """
    def __init__(self, templatefile=None):
        # Words used to break up clauses
        self.preconditions = ['stat', 'status', 'random', 'timer']
        self.actions = ['cast', 'attack', 'flee', 'move', 'say', 'wait', 'wander', 'follow']
        self.target = ['self', 'nearest', 'farthest', 'any']
        self.conditions = ['has', 'lacks', 'stat', 'status', 'faction']
        self.parse_words = self.preconditions + self.actions + self.target + self.conditions

        self.templatefile = templatefile
        self.data = {'filename': templatefile}
        if templatefile:
            self._initialize()

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
                base_dict[sections[i]] = self.split_clauses(unspaced[number + 1:])
            else:
                base_dict[sections[i]] = self.split_clauses(unspaced[number + 1:indices[i + 1]])
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

    def split_clauses(self, lines):
        """
        :param lines: lines in 'combat' or 'idle' sections
        :return: list of dictionaries
        """
        line_list = []
        for line in lines:
            base_dict = {'precondition': None, 'action': None, 'target': None, 'condition': None}
            try:
                words = [word.strip() if '(' not in word and ')' not in word and ',' not in word
                         else eval(word) for word in line.split()]
            except SyntaxError:
                print('Check that coords move statement tuple like (3,3) not (3, 3)')
                raise
            sections = [word for word in words if word in self.parse_words]
            indices = [i for i, word in enumerate(words) if word in self.parse_words]
            for i, number in enumerate(indices):
                if i + 1 == len(indices):
                    base_dict[self.word_type(sections[i], i)] = words[number:]
                else:
                    base_dict[self.word_type(sections[i], i)] = words[number:indices[i + 1]]
            line_list.append(base_dict)

        # Post clean up
        for dict in line_list:
            for section, clause in dict.items():
                if clause:
                    if clause[0] == 'say':
                        dict[section] = [clause[0], ' '.join(clause[1:])]
        return line_list

    def word_type(self, word, index):
        if word in self.preconditions and index == 0:
            return 'precondition'
        elif word in self.actions:
            return 'action'
        elif word in self.target:
            return 'target'
        elif word in self.conditions:
            return 'condition'
        else:
            return None

    @staticmethod
    def list_lines_from_template(filename):
        with open(filename, 'r') as template_file:
            return [line.strip('\n') for line in template_file.readlines()]