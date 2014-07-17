#!/usr/bin/env python3

'''
The idea: Create a phylogenetic tree structure. Allow the use to pin data
to the tree. This program keeps track of which files are related to which
nodes, it does not hold the data. Rather it hardlinks all the data into a local
.data folder. It pickles the tree structure for persistence.
'''

import argparse

__version__ = "0.0.0"

# ==============
# Infrastructure
# ==============

class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '-v', '--version',
            action='version',
            version='%(prog)s {}'.format(__version__)
        )
        subparsers = self.parser.add_subparsers(
            metavar='[ for help on each: %(prog)s <subcommand> -h ]',
            title='subcommands'
        )

        Add(
            subparsers.add_parser(
                'add',
                help='add a data file'
            )
        )

        Ls(
            subparsers.add_parser(
                'ls',
                help='list the contents of pyb database'
            )
        )

        Get(
            subparsers.add_parser(
                'get',
                help='symlink data from PYBDB to working directory'
            )
        )

        self.args = self.parser.parse_args()

class Subcommand:
    def __init__(self, parser):
        self.parser = parser
        self._parse()
        self.parser.set_defaults(func=self.func)

    def _parse(self, parser):
        raise NotImplemented

    def func(self):
        raise NotImplemented

class Get(Subcommand):
    def _parse(self):
        pass

    def func(self, args):
        print('get')

class Ls(Subcommand):
    def _parse(self):
        self.parser.add_argument(
            '-T', '--print-tags',
            help='list of tags to print',
            nargs='+'
        )

    def func(self, args):
        print('ls')

class Add(Subcommand):
    def _parse(self):
        self.parser.add_argument(
            '-f', '--file',
            help='Data filename',
            type=argparse.FileType('r')
        )
        self.parser.add_argument(
            '-n', '--sciname',
            help='Taxon scientific name'
        )
        self.parser.add_argument(
            '-d', '--taxon-id',
            help='Taxon id'
        )
        self.parser.add_argument(
            '-g', '--guess-id',
            help='Guess the sciname from the filename',
            action='store_true',
            default=False
        )
        self.parser.add_argument(
            '-t', '--tags',
            help='peg tags and values to data (<tag>="<value>")',
            nargs="+"
        )
        self.parser.add_argument(
            '-k', '--schema',
            help='set read schema for the datatype from a file',
            type=argparse.FileType('r')
        )
        self.parser.add_argument(
            '-m', '--copy-method',
            help='choose to move(m), copy(c), hard link(l) or ' +
                 'symlink(s) the data to PYBHOME',
            choices=['s', 'l', 'c', 'm']
        )

    def func(self, args):
        print('add')


# =============
# Data Handling
# =============

class Node():
    def __init__(self):
        self.children = set()
        self.parent = None
        self.tags = {}
        self.data = set()

class DataCollection()
    def __init__(self, parent):
        self.parent = parent
        self.children = set()

class Datum():
    def __init__(self, parent):
        self.parent = parent


if __name__ == '__main__':
    args = Parser().args
    args.func(args)
