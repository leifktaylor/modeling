import os
from gameobject import save_lifeform, create_lifeform_from_template


def calculate_stats(STR, MND, STA, SPD):
    # Base values
    HP = 5
    MP = 5
    PDEF = 1
    MDEF = 1

    HP = int(HP + (.75 * STA))
    MP = int(MP + (.75 * MND))
    MDEF = int(MDEF + ((.5 * MND) + .25 * SPD))
    PDEF = int(PDEF + ((.5 * STR) + .25 * SPD))
    return HP, MP, PDEF, MDEF

print('Generate Player Template from input')

# Input name and description
while True:
    lifeform_type = 'lifeform_type:LifeForm'
    name = 'name:' + raw_input('Player name: ')
    description = 'description:' + raw_input('Description: ')
    choice = raw_input('Confirm choices? y/n: ')
    if choice.lower() == 'y':
        break

while True:
    proposal = int(raw_input('Power level (determines stat_points to spend): 1-100: '))
    if proposal > 100:
        proposal = 100
    elif proposal < 0:
        proposal = 1
    stat_points = proposal * 5

    re_run = False
    print('')
    print('Choose stat allocation for STR, MND, STA and SPD.  These core stats will effect auxilliary stats')
    print('Total Points: {0}'.format(stat_points))
    try:
        stat_dict = {}
        for item in ['STR', 'MND', 'STA', 'SPD']:
            stat_dict[item] = int(raw_input('{0}: '.format(item)))
            stat_points -= stat_dict[item]
            print('Remaining points: {0}'.format(stat_points))
    except ValueError:
        print('Must enter numerical value!')
        re_run = True
    if stat_points < 0:
        re_run = True
        print('Used too many stat points! Try again')
    elif stat_points > 0:
        re_run = True
        print('You still have {0} unspent stat points! Try again'.format(stat_points))
    if re_run:
        pass
    else:
        HP, MP, PDEF, MDEF = calculate_stats(stat_dict['STR'], stat_dict['MND'], stat_dict['STA'], stat_dict['SPD'])
        print('Calculating stats...')
        print('')
        print('HP: {0}'.format(HP))
        print('MP: {0}'.format(MP))
        print('PDEF: {0}'.format(PDEF))
        print('MDEF: {0}'.format(MDEF))
        choice = raw_input('Confirm stat allocation? y/n: ')
        if choice.lower() == 'y':
            STR = 'STR:{0}'.format(stat_dict['STR'])
            MND = 'MND:{0}'.format(stat_dict['MND'])
            STA = 'STA:{0}'.format(stat_dict['STA'])
            SPD = 'SPD:{0}'.format(stat_dict['SPD'])
            HP = 'HP:{0}'.format(HP)
            MP = 'MP:{0}'.format(MP)
            MDEF = 'MDEF:{0}'.format(MDEF)
            PDEF = 'PDEF:{0}'.format(PDEF)
            break

while True:
    filename = raw_input('Character Filename to create: ')
    if '.lfm' not in filename:
        filename = '{0}.lfm'.format(filename)
    choice = raw_input('Confirm filename? y/n: ')
    if choice.lower() == 'y':
        break

cwd = os.getcwd()
filepath = '{0}/lifeform/{1}'.format(cwd, filename)
with open(filepath, 'w+') as f:
    for line in [name, lifeform_type, description, STR, STA, MND, SPD, HP, MP, MDEF, PDEF]:
        f.write('{0}\n'.format(line))
    f.close()

lifeform_instance = create_lifeform_from_template(filepath)
save_lifeform(lifeform_instance, '{0}.sav'.format(name.replace('name:', '')))
