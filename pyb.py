#!/usr/bin/env python3

'''
The idea: Create a phylogenetic tree structure. Allow the use to pin data
to the tree. This program keeps track of which files are related to which
nodes, it does not hold the data. Rather it hardlinks all the data into a local
.data folder. It pickles the tree structure for persistence.
'''

import argparse
import os
import sys
import pickle

__version__ = "0.0.0"
__prog__ = 'pyb'

# ==============
# Infrastructure
# ==============

class OSVars:
    HOME = 'PYBHOME'
    DATA_DIR = '.data'
    BLAST_DIR = 'blastdb'
    FILE_DIR = 'files'
    DATA = 'pyb.dat'

class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '-v', '--version',
            action='version',
            version='{} {}'.format(__prog__, __version__)
        )
        subparsers = self.parser.add_subparsers(
            metavar='[ for help on each: {}s <subcommand> -h ]'.format(__prog__),
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
    def __init__(self, parent):
        self.parent = parent
        self.children = set()
        self.tags = {}

    def add_child(self, child):
        self.children.add(child)

    def remove_child(self, child):
        self.children.remove(child)

    def get_tag(self, tag):
        try:
            return(self.tags[tag])
        except KeyError:
            return(None)

    def set_tag(self, tag, value):
        self.tags[tag] = value

class DataHoldingNode(Node):
    def __init__(self, **kwargs):
        super.__init__(**kwargs)
        self.data = set()

class Taxon(DataHoldingNode):
    def __init__(self, taxid, sciname, common=None, syn=set(), **kwargs):
        super.__init__(*args, **kwargs)
        self.taxon_id = taxid
        self.scientific_name = sciname
        self.common_name = common
        self.synonyms = syn

class Datum(Node):
    def __init__(self, filename, **kwargs):
        super.__init__(**kwargs)
        self.filename = filename
        self.uuid = None
        self.child = None

    def make_uuid(self):
        '''
        Calculate md5 checksum for the data, this will be used as the unique
        identifier.
        '''
        pass

class Seq(Datum):
    def __init__(self, alphabet, **kwargs):
        super.__init__(**kwargs)
        self.alphabet = alphabet
        self.blastname = None
        self.annotations

    def prepare_blastdb(self):
        pass



# =========
# Utilities
# =========

def err(msg, status=1):
    print(msg, file=sys.stderr)
    sys.exit(status)


if __name__ == '__main__':
    try:
        home = os.environ[OSVars.HOME]
    except KeyError:
        err('No PYBHOME environmental variable found')

    try:
        datapath = os.path.join(home, '.data')
        if not os.path.exists(datapath):
            os.makedirs(datapath)
    except OSError:
        err("Cannot create directory '{}'".format(datapath))

    root = Node(parent=None)
    args = Parser().args
    args.func(args)
