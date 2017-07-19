#!/usr/bin/env python
# * coding: utf8 *
'''
yaml.py

A module that strips out the old wordpress yaml items
'''
import os
import sys
import ruamel.yaml as yaml

unused_keys = ['author_login', 'author_email', 'wordpress_id', 'wordpress_url', 'date_gmt']
unused_author_keys = ['login', 'url']
useless_tags = [
    'utah', 'gis', 'map', 'mapping', 'points', 'dataset', 'download', 'agrc', 'layer', 'shapefile', 'geodatabase', 'metadata', 'shp', 'gdb', 'kml', 'lyr',
    'digital', 'geographic', 'information', 'database', 'state', 'statewide', 'category', 'services', 'daas', 'locations', 'SDE', 'sgid', 'vector', 'esri',
    'fb sgid elevation terrain gis data', 'arcgis', 'agrc nsgic gis', 'atlas.utah.gov', 'web', 'gis.utah.gov', 'basemaps', 'street', 'geocdoing', 'gps',
    'surveying', 'geocodes', 'spotlight', 'interactive', 'coordinate', 'ut', '2013', 'use', 'upgrade', 'map spotlight', 'maturity', 'tag', 'centerlined',
    'stateiwide', 'gid', 'geogrpahic', '10.3', 'utah vector', 'find', 'digital download', 'mail', 'flown', 'plan', 'load', 'trends',
    'watershed restoration initiative', 'webmercator', 'blog', '1 meter', 'composite', 'geogoding', 'overview'
]


def pluck_content(f):
    #: file should already be seeked to last yaml separater
    pointer = f.tell()

    #: create generator to read to the end of the file
    readline = iter(f.readline, '')
    readline = iter(readline.next, '')

    return ''.join(readline)


def pluck_yaml(f):
    pointer = f.tell()

    if f.readline() != '---\n':
        f.seek(pointer)

        return ''

    readline = iter(f.readline, '')
    readline = iter(readline.next, '---\n')

    return ''.join(readline)


def prune_keys(front_matter):
    keys = front_matter.keys()

    for key in keys:
        if key in unused_keys:
            front_matter.pop(key, None)

    if 'author' in keys:
        sub_keys = front_matter['author'].keys()
        for key in sub_keys:
            if key in unused_author_keys:
                front_matter['author'].pop(key, None)

    return front_matter


def prune_tags(front_matter):
    tags = front_matter['tags']

    ok_tags = set([x.lower() for x in tags if x not in useless_tags])
    ok_tags = list(ok_tags)
    ok_tags.sort()

    return ok_tags


def discover_files(walk_dir):
    print('walk_dir = ' + walk_dir)
    print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

    for root, subdirs, files in os.walk(walk_dir):
        if (root.startswith(walk_dir + 'images') or root.startswith(walk_dir + '_site') or root.startswith(walk_dir + 'downloads') or
                root.startswith(walk_dir + '.grunt')):
            continue

        for filename in files:
            _, extension = os.path.splitext(filename)
            if extension.lower() not in ['.html', '.md']:
                continue

            file_path = os.path.join(root, filename)

            print('\t- file %s (full path: %s)' % (filename, file_path))

            with open(file_path, 'r') as original, open(file_path + '.bak', 'w') as updated:
                front_matter = yaml.load(pluck_yaml(original), Loader=yaml.Loader)

                if front_matter is None:
                    print('skipping {}'.format(original))
                    os.rename(file_path + '.bak', file_path)
                    continue

                front_matter = prune_keys(front_matter)
                front_matter['tags'] = prune_tags(front_matter)

                front_matter = yaml.dump(front_matter, Dumper=yaml.RoundTripDumper, block_seq_indent=2, default_flow_style=False, indent=2)
                content = pluck_content(original)

                updated.write('---\n')
                updated.write(front_matter)
                updated.write('---\n')

                updated.write(content)

            os.rename(file_path + '.bak', file_path)


if __name__ == '__main__':
    discover_files(sys.argv[1])
