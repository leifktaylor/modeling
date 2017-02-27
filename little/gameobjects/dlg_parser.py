"""
Well aren't you a [handsome] one! Would you like to meet my [daughter]?
[daughter]
Yes my daughter! Why she's the finest lass in this fair city.  If only I could find her a [suitor]
[handsome]
Yes! You're so incredibly handsome.. heck I'd date you!
[suitor]
Yes! Why don't you go meet her! She's somewhere in this weird place.
Give her this!
{give misc/dildo.itm}
{dialogue template2.dlg}
"""


def list_lines_from_template(filename):
    with open(filename, 'r') as template_file:
        return [line.strip('\n') for line in template_file.readlines()]


def template_lines_to_dict(line_list):

    # Get rid of all comments in all lines
    uncommented = [line.split('#', 1)[0].rstrip() for line in line_list]
    # Get rid of empty lines
    unspaced = [line for line in uncommented if line]

    indices = [i for i, item in enumerate(unspaced) if item[0] == '[' and item[-1] == ']' and i is not 0]
    sections = [unspaced[i: j] for i, j in zip([0] + indices, indices + [None])]
    # convert to dictionary with section headers as keys
    return {sections[i][0].replace('[', '').replace(']', '').strip(): sections[i][1:]
            for i, item in enumerate(sections)}


def dict_lines(filename):
    return template_lines_to_dict(list_lines_from_template(filename))

