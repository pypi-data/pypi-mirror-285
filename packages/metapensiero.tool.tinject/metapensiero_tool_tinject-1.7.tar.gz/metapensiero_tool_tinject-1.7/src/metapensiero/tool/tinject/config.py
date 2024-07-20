# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Configuration details
# :Created:   gio 21 apr 2016 18:22:20 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2018, 2024 Lele Gaifax
#

from ruamel import yaml


class Constructor(yaml.Constructor):
    pass


def include(loader, node):
    path = loader.construct_scalar(node)
    fullpath = include.basedir / path
    return fullpath.read_text('utf-8')

Constructor.add_constructor('!include', include)


class Config(object):
    @classmethod
    def from_yaml(cls, fname):
        include.basedir = fname.parent
        with fname.open() as stream:
            loader = yaml.YAML()
            loader.Constructor = Constructor
            content = loader.load_all(stream)
            globals = next(content)
            try:
                actions = next(content)
            except StopIteration:
                actions = globals
                globals = {}
        return cls(globals, actions)

    def __init__(self, globals, actions):
        self.globals = globals
        self.actions = actions

    def write(self, output):
        with output.open('w') as stream:
            yaml.dump_all([self.globals, self.actions], stream,
                          default_style="|",
                          default_flow_style=False)
