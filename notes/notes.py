# Musical Notes Program


class Note(object):
    def __init__(self, current_name='C', base_name='C', current_number=0, base_number=0, type='natural', octave=4):
        self.base_name = base_name
        self.current_name = current_name
        self.base_number = base_number
        self.current_number = current_number
        self.type = type
        self.octave = octave

    def description(self):
        """
        Return dictionary of note's information like name and number
        """
        return {'name': self.current_name, 'number': self.current_number}

    def set_number(self, number):
        """
        Sets the note's number to given number.
        :param number: number to change note to
        :return:
        """
        # SO CONFUSED!!
        if number < 0:
            corrected_number = range(self.current_number, 12)[-(abs(number) % 12)]
        else:
            corrected_number = self.current_number + number % 12
        print(corrected_number)
        self.current_number = corrected_number

    def _set_current_name(self):
        distance_from_base = self.current_number - self.base_number
        # If the note is sharped
        if distance_from_base > 0:
            self.current_name = self.base_name + ('#' * distance_from_base)
        # If the note is flatted
        elif distance_from_base < 0:
            self.current_name = self.base_name + ('b' * abs(distance_from_base))
        #If the note is unchanged
        else:
            self.current_name = self.base_name

    def _get_number_from_name(self):
        # Confirm name doesn't have mixed accidentals
        if '#' in self.current_name and 'b' in self.current_name:
            raise RuntimeError('Name: {0}, contains sharps and flats!'.format(self.current_name))
        elif '#' in self.current_name:
            self.current_number = self.base_number + self.current_name.count('#')
        elif 'b' in self.current_name:
            self.current_number = self.base_number - self.current_name.count('b')
        else:
            self.current_number = self.base_number

    def flat_note(self):
        self.set_number(-1)
        self._set_current_name()

    def sharp_note(self):
        self.set_number(1)
        self._set_current_name()


class Scale(object):
    pass