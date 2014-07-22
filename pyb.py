#!/usr/bin/env python3

'''
The idea: Create a phylogenetic tree structure. Allow the use to pin data
to the tree. This program keeps track of which files are related to which
nodes, it does not hold the data. Rather it hardlinks all the data into a local
.pybdata folder. It pickles the tree structure for persistence.
'''

import argparse
import os
import sys
import shutil
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from src.Taxon import *
from src.err import err

__version__ = "0.0.0"
__prog__ = 'pyb'

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
        Util(sp, 'util', 'miscellaneous utilities')

        self.args = self.parser.parse_args()


# ==============
# Infrastructure
# ==============

class Entrez:
    BASE   = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils'
    EFETCH = '{}/efetch.fcgi'.format(BASE)

    @classmethod
    def taxid2lineage(cls, taxids):
        url = '{}?db=taxonomy&id={}'.format(cls.EFETCH, '+'.join(taxids))
        xmldata = ''.join([s.decode('utf-8') for s in urlopen(url).readlines()])
        root = ET.fromstring(xmldata)
        lineages = []
        for taxon in root.findall('./Taxon'):
            taxid = taxon.find('TaxId').text
            sciname = taxon.find('ScientificName').text
            lineage = Taxon()
            # Starting from root, build lineage
            for ancestor in taxon.findall('./LineageEx/Taxon'):
                t = ancestor.find('TaxId').text
                s = ancestor.find('ScientificName').text
                lineage = Taxon(parent=lineage, taxid=t, sciname=s)
            # Add species (since entrez lineages annoyingly leave self off)
            lineage = Taxon(parent=lineage, taxid=taxid, sciname=sciname)
            lineages.append(lineage)
        return(lineages)

class OSVars:
    _HOME = 'PYBHOME'
    _DATA_DIR = 'pybdata'
    _DATA = 'pybtree.pkl'

    @classmethod
    def get_home_dir(cls):
        try:
            home = os.environ[cls._HOME]
        except KeyError:
            err('No PYBHOME environmental variable found')
        return(home)

    @classmethod
    def get_data_dir(cls):
        try:
            homedir = cls.get_home_dir()
            datadir = os.path.join(homedir, cls._DATA_DIR)
        except OSError:
            err("Cannot create directory '{}'".format(datapath))
        return(datadir)

    @classmethod
    def get_pkl(cls):
        homedir = cls.get_home_dir()
        pkl = os.path.join(homedir, cls._DATA)
        return(pkl)


# ===========
# Subcommands
# ===========

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
        )
        self.parser.add_argument(
            'taxon',
            help="taxid or name (e.g. 4577 or Zea_mays), can add subfolder (e.g. 4577/ecotypes)",
        )

    def func(self, args, root):
        taxondir = os.path.join(OSVars.get_data_dir(), args.taxon)
        if not os.path.exists(taxondir):
            try:
                os.mkdir(taxondir)
            except OSError as e:
                err(e)
            root.add_taxon(Entrez.taxid2lineage([args.taxon])[0])

        for f in args.infiles:
            src = os.path.abspath(f)
            try:
                dst = os.path.join(taxondir, os.path.basename(f))
                if not os.path.isfile(src):
                    raise OSError
                os.symlink(src, dst)
            except OSError:
                err("Could not symlink '{}' to '{}'".format(src, dst))

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

    def func(self, args, root):
        print('put')

class Ls(Subcommand):
    def _parse(self):
        self.parser.add_argument(
            'files',
            help='files to ls'
        )

    def func(self, args, root):
        print('ls')

class Util(Subcommand):
    def _parse(self):
        # TODO rewrite these as util subcommands
        self.parser.add_argument(
            '--delete-tree',
            help='deletes the phylogenetic tree',
            action='store_true',
            default=False
        )
        self.parser.add_argument(
            '--rebuild-tree',
            help='rebuilds the phylogenetic tree',
            action='store_true',
            default=False
        )
        self.parser.add_argument(
            '--clear-all',
            help='destroys tree and clears all data',
            action='store_true',
            default=False
        )
        self.parser.add_argument(
            '--taxonomy-validation',
            help='looks for misplaced files',
            action='store_true',
            default=False
        )

    def func(self, args, root):
        if args.delete_tree or args.clear_all:
            try:
                os.remove(OSVars.get_pkl())
            except OSError:
                pass

        if args.clear_all:
            try:
                shutil.rmtree(OSVars.get_data_dir())
            except OSError:
                pass



if __name__ == '__main__':

    pkl = OSVars.get_pkl()
    root = unpickle_taxon(pkl)

    datadir = OSVars.get_data_dir()
    if not os.path.exists(datadir):
        os.mkdir(datadir)

    args = Parser().args
    args.func(args, root)

    root.printall()

    pickle_taxon(root, pkl)
