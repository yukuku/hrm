import codecs
import json
import os

with codecs.open('../extras/original_levels.json', encoding='utf-8') as f:
    levels = json.load(f)
    for level in levels:
        number = level.get('number')
        name = level.get('name')
        instructions = level.get('instructions')
        commands = level.get('commands')
        floor = level.get('floor')
        examples = level.get('examples')
        challenge = level.get('challenge')

        os.mkdir('../levels/original/{}'.format(number))

        with codecs.open('../levels/original/{}/q.txt'.format(number), 'w', encoding='utf-8') as fo:
            fo.write(u'// Original level {}: {}'.format(number, name))


