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
    DATA = 'pyb.pkl'

class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '-v', '--version',
            action='version',
            version='{} {}'.format(__prog__, __version__)
        )

        sp = self.parser.add_subparsers(
            metavar='[ for help on each: {}s <subcommand> -h ]'.format(__prog__),
            title='subcommands'
        )

        Put(sp, 'put', 'add a data file')
        Get(sp, 'get', 'symlink data from PYBDB to working directory')
        Ls(sp, 'ls', 'list the contents of pyb database')

        self.args = self.parser.parse_args()

class Subcommand:
    def __init__(self, subparser, cmd, desc):
        self.parser = subparser.add_parser(cmd, help=desc)
        self._parse()
        self.parser.set_defaults(func=self.func)

    def _parse(self, parser):
        raise NotImplemented

    def func(self):
        raise NotImplemented

class Put(Subcommand):
    def _parse(self):
        self.parser.add_argument(
            'infiles',
            help='files to add',
            nargs='+',
            type=argparse.FileType('r')
        )
        self.parser.add_argument(
            'taxon',
            help="taxid or name (e.g. 4577 or Zea_mays), can add subfolder (e.g. 4577/ecotypes)",
        )

    def func(self, args):
        print('put')

class Get(Subcommand):
    def _parse(self):
        self.parser.add_argument(
            'from',
            help='files to copy out (e.g. rosids/*.faa)',
            nargs='+',
        )
        self.parser.add_argument(
            'to',
            help="path in filesystem to copy to (e.g. '.')",
        )

    def func(self, args):
        print('put')

class Ls(Subcommand):
    def _parse(self):
        self.parser.add_argument(
            'files',
            help='files to ls'
        )

    def func(self, args):
        print('ls')


# =============
# Data Handling
# =============

class Taxon():
    def __init__(self, parent, taxid, sciname, common=None, syn=set(), **kwargs):
        self.parent = parent
        self.children = set()
        self.taxon_id = taxid
        self.scientific_name = sciname
        self.common_name = common
        self.synonyms = syn

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

    @classmethod
    def get_scinames(cls, taxids):
        raise NotImplemented

    @classmethod
    def get_taxids(cls, scinames):
        raise NotImplemented

    @classmethod
    def get_lineages(cls, taxids):
        raise NotImplemented


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


    pkl = os.path.join(home, OSVars.DATA)

    try:
        f = open(pkl, 'rb')
        root = pickle.load(f)
        f.close()
    except IOError:
        root = Taxon(parent=None, taxid=0, sciname='root')
    except Exception as e:
        err('unknown pickle error\n{}'.format(e))

    args = Parser().args
    args.func(args)

    with open(pkl, 'wb') as f:
        pickle.dump(root, f)
