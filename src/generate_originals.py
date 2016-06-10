import codecs
import json
import os

with codecs.open('../extras/original_levels.json', encoding='utf-8') as f:
    levels = json.load(f)
    for level in levels:
        number = level.get('number')

        if level.get('cutscene'):
            continue

        name = level.get('name')
        instructions = level.get('instructions')
        commands = level.get('commands')
        floor = level.get('floor')
        examples = level.get('examples')
        challenge = level.get('challenge')

        dirname = '../levels/original/{}'.format(number)
        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        print dirname

        with codecs.open('../levels/original/{}/q.txt'.format(number), 'w', encoding='utf-8') as fo:
            fo.write(u'// Original level {}: {}\n'.format(number, name))
            if challenge:
                fo.write(u'// Challenge: {}/{}\n'.format(challenge['size'], challenge['speed']))
            fo.write(u'//\n')

            for ln in instructions.splitlines():
                fo.write(u'// {}\n'.format(ln))
            fo.write(u'\n')

            for command in commands:
                fo.write(u'{}\n'.format(command.lower()))
            fo.write(u'\n')

            if floor:
                fo.write(u'mem size {}\n'.format(int(floor['columns']) * int(floor['rows'])))
                tiles = floor.get('tiles')
                if tiles:
                    if isinstance(tiles, list):
                        for i, tile in enumerate(tiles):
                            fo.write(u'mem[{}] = {}\n'.format(i, tile))
                    elif isinstance(tiles, dict):
                        for k, tile in tiles.iteritems():
                            fo.write(u'mem[{}] = {}\n'.format(k, tile))

        for i, ex in enumerate(examples):
            with codecs.open('../levels/original/{}/sample{}.in'.format(number, i), 'w', encoding='utf-8') as finn, codecs.open('../levels/original/{}/sample{}.out'.format(number, i), 'w', encoding='utf-8') as fout:
                desc = ex.get('desc')
                if desc:
                    finn.write(u'// {}\n\n'.format(desc))

                for box in ex['inbox']:
                    finn.write(u'{}\n'.format(box))
                for box in ex['outbox']:
                    fout.write(u'{}\n'.format(box))





