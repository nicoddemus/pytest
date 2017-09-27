from __future__ import absolute_import, division, print_function, unicode_literals

import pathlib

files = pathlib.Path('../testing').glob('test*.py')

for path in files:
    lines = path.read_text(encoding='utf-8').splitlines()
    index = 0
    inside_func = False
    new_lines = []
    while index < len(lines):
        line = lines[index]
        if line.strip().startswith('def '):
            new_lines.append(line)
            indent = line.index('def')
            new_lines.append(indent * ' ' + '    return\n')
        else:
            new_lines.append(line)

        index += 1

    print(path.name)
    pathlib.Path(path.name).write_text('\n'.join(new_lines), encoding='utf-8')


