import game_constants


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
