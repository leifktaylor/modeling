import subprocess

ch_dir = '.'

def cmd(cmd):
    """
    Executes a command in the termina and saves the output to a list of lines.
    :param cmd:
    :return:
    """
    global ch_dir
    try:
        print('Current Directory: {0}'.format(ch_dir))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=ch_dir)
        lines = p.stdout.readlines()
        line_list = []
        for line in lines:
            try:
                line_list.append(line.decode('ascii').strip('\r\n'))
            except UnicodeDecodeError:
                line_list.append(line.strip(b'\r\n'))
        return line_list
    except NotADirectoryError:
        print('Directory Invalid')
        return []


def parse_input(input_string):
    global ch_dir
    if input_string.split()[0] == 'cd':
        try:
            cd_arg = input_string.split()[1]
            if cd_arg == '..':
                ch_dir = cd_arg
                #or back slash .. todo
            elif cd_arg == '/' or cd_arg == '\\':
                ch_dir = 'C:\\'
            else:
                # todo ... this logic is annoying as fuck
                pass
            ch_dir = input_string.split()[1]
        except IndexError:
            print('hmm...')
    r = cmd(input_string)
    for line in r:
        print(line)


while True:
    input_string = str(input('@:'))
    parse_input(input_string)
