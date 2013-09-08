'''rugmigen.py: rugmi code generator

Builds a single rugmi.py based on a list of plugins.

Does some basic dependency tracking with extremely basic python parsing.
'''

USAGE = """Usage: {0} <output file> <plugins or presets>
Examples:
    {0} output.py config core parse_form index routing main
    {0} output.py DEFAULTS
    {0} output.py DEFAULTS -index
"""

PRESETS = {
    'DEFAULTS': "config core parse_form index routing main",
}

HEADER = """#!/usr/bin/env python
# Automatically generated by rugmigen.py
# Plugins used: %s

"""

import os
import re
import sys
import itertools

class UnmetDependenciesError(Exception):
    pass

def flatten(l):
    return list(itertools.chain(*l))


def check_import(line, tracker):
    '''Checks if a line is an internal rugmi import or a normal python one
    Returns True if the line should be skipped from the final output because
    it was processed as either kind of import'''

    # this kind of import specifies a rugmi dependency
    match = re.match(r"^from rugmi\.plugins\.(.*) import .*$", line)
    if match:
        tracker["depends"].append(match.group(1))
        return True

    match = re.match("^(import .*|from .* import .*)$", line)
    if match:
        # save the line to send it to the top of the file later
        tracker["imports"].append(line)
        return True

    return False


def parse_plugin(filename):
    '''Parses a plugin, extracts metadata and its code section.'''

    code = []

    # the "provides" value starts the same unless a plugin overrides it
    provides = filename

    # dependency tracker information
    tracker = {
        'depends': [],
        'imports': [],
    }

    full_filename = "plugins/%s.py" % filename
    try:
        fd = open(full_filename)
    except IOError:
        raise UnmetDependenciesError("Can't open %s" % full_filename)

    for line in fd:
        line = line.rstrip()

        skip = False
        provides_string = "# rugmi: provides:"
        # this line is probably an import! probably.
        if line.startswith("import ") or line.startswith("from "):
            skip = check_import(line, tracker)

        elif line.startswith(provides_string):
            skip = True
            provides = line[len(provides_string):].strip()

        if not skip:
            code.append(line)

    return (filename, provides, code, tracker)


def check_depends(plugin_list):
    '''Checks if all the specified dependencies are met

    Raises UnmetDependenciesError otherwise'''

    all_provides = set([x[1] for x in plugin_list])
    for plugin in plugin_list:
        unmet = set(plugin[3]['depends']) - set(all_provides)
        if unmet:
            raise UnmetDependenciesError('%s requires %s' %
                (plugin[0], ', '.join(unmet)))


def write_imports(output_fd, plugin_list):
    '''Write all the imports nicely at the top of the file'''

    imports = flatten([x[3]['imports'] for x in plugin_list])
    imports = list(set(imports))
    imports.sort(key=lambda x: len(x))

    imports_text = '\n'.join(imports)
    output_fd.write(imports_text)


def write_codeblocks(output_fd, plugin_list):
    '''Write each block of extracted code, in order'''

    for plugin in plugin_list:
        output_fd.write('\n'.join(plugin[2]) + "\n")


def generate(output_filename, name_list):
    plugin_list = []

    for filename in name_list:
        plugin_list.append(parse_plugin(filename))

    check_depends(plugin_list)

    output_fd = open(output_filename, "w")
    output_fd.write(HEADER % (' '.join(name_list)))

    write_imports(output_fd, plugin_list)

    write_codeblocks(output_fd, plugin_list)

    output_fd.close()

def parse_args(args):
    name_list = list()
    for name in args:
        if name.isupper():
            if name not in PRESETS:
                raise UnmetDependenciesError("Unknown preset %s" % name)
            name_list.extend(PRESETS[name].split())
        elif name.startswith("-"):
            name_list.remove(name[1:])
        else:
            name_list.append(name)
    return name_list

def main():
    if len(sys.argv) < 3:
        print(USAGE.format(os.path.basename(sys.argv[0])))
        return
    output_filename = sys.argv[1]

    try:
        name_list = parse_args(sys.argv[2:])
        print("Generating %s with plugins %s" %
            (output_filename, ', '.join(name_list)))

        generate(output_filename, name_list)
    except UnmetDependenciesError as e:
        print("Error: Unmet dependencies: %s" % str(e))
    else:
        print("Success")

if __name__ == '__main__':
    main()
