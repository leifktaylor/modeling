"""
Parse .rm (room) template file and return dictionary of parameters
"""


def list_lines_from_template(filename):
    with open(filename, 'r') as template_file:
        return [line.strip('\n') for line in template_file.readlines()]


def template_lines_to_dict(line_list):
    base_dict = {'settings': {'atenter': None, 'atexit': None, 'look': None, 'listen': None, 'name': None},
                 'lifeforms': None, 'items': None, 'links': None}

    # Get rid of all comments in all lines
    uncommented = [line.split('#', 1)[0].rstrip() for line in line_list]
    # Get rid of empty lines
    unspaced = [line for line in uncommented if line]

    # divide into sections (section markers in .rm file are '*** section_name ***')
    indices = [i for i, item in enumerate(unspaced) if '***' in item and i is not 0]
    sections = [unspaced[i + 1: j] for i, j in zip([0] + indices, indices + [None])]

    try:
        settings = sections[0]
        base_dict['lifeforms'] = sections[1]
        base_dict['items'] = sections[2]
        base_dict['links'] = sections[3]
    except IndexError:
        raise RuntimeError('rm file must contain "settings", "lifeforms", "items", and "links" sections, even if empty')

    try:
        settings_dict = {line.split(':')[0]: line.split(':')[1] for line in settings}
    except IndexError:
        raise RuntimeError('Cannot parse settings, make sure format is <parameter>:<value> for each line in settings')

    # Convert strings of digits to integers, and string booleans to python booleans
    for k, v in settings_dict.items():
        if v.isdigit():
            settings_dict[k] = int(settings_dict[k])
        elif v.lower() in ['yes', 'true']:
            settings_dict[k] = stringtobool(settings_dict[k])
    base_dict['settings'].update(settings_dict)

    return base_dict


def stringtobool(string):
    return string.lower() in ['yes', 'true']


def dict_lines(filename):
    """
    Takes a .itm file and parses human readable format into a dictionary
    :param filename: file name in proper .itm format
    :return: dictionary
    """
    return template_lines_to_dict(list_lines_from_template(filename))
