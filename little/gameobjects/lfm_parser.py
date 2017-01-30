import game_constants
import re


def list_lines_from_template(filename):
    with open(filename, 'r') as template_file:
        return [line.strip('\n') for line in template_file.readlines()]


def template_lines_to_dict(line_list):
    base_dict = {stat: None for stat in game_constants.possible_stats}

    # Get rid of all comments in all lines
    uncommented = [line.split('#', 1)[0].rstrip() for line in line_list]
    # Get rid of empty lines
    unspaced = [line for line in uncommented if line]

    # Convert lines into a dictionary
    try:
        line_dict = {line.split(':')[0]: line.split(':')[1] for line in unspaced}
    except IndexError:
        raise RuntimeError('Cannot parse template, make sure format is <parameter>:<value> for each line')

    # Convert strings of digits to integers, and string booleans to python booleans
    for k, v in line_dict.items():
        if v.isdigit():
            line_dict[k] = int(line_dict[k])
        elif v.lower() in ['yes', 'true']:
            line_dict[k] = stringtobool(line_dict[k])

    # Find and correct item slot lines
    if 'slots' in line_dict.keys():
        if line_dict['slots'] is not None:
            slots_list = [None]*int(line_dict['slots'])
            for k, v in line_dict.items():
                item_slot = re.search('slot\d+', k)
                if item_slot:
                    slot_key = item_slot.group(0)
                    slot_index = int(re.sub('\D', '', slot_key))
                    # slot_value will look like: path/to/item True 20
                    params = v.split()
                    params[1] = stringtobool(params[1])
                    params[2] = int(params[2])
                    slots_list[slot_index] = {'path': params[0], 'equipped': params[1], 'drop_rate': params[2]}
    else:
        slots_list = []
    # cleanup parsed out entries
    for k, v in line_dict.items():
        if 'slot' in k and k != 'slots':
            line_dict.pop(k)
    line_dict['inventory'] = slots_list

    base_dict.update(line_dict)
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
