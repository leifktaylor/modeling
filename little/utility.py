def convert_to_ascii(input):
    """
    Convert unicode dictionary, list or string into ascii
    :param input: input string, list or dictionary object
    :return: object where all strings are converted to ascii
    """
    if isinstance(input, dict):
        return {convert_to_ascii(key): convert_to_ascii(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert_to_ascii(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
