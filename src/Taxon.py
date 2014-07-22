#!/usr/bin/env python3

import sys
import pickle
from src.err import err

class Taxon():
    def __init__(self,
                 parent=None,
                 taxid=0,
                 sciname='root',
                 common=None,
                 syn=set()
                ):
        self.parent = parent
        self.children = set()
        self.taxid = taxid
        # try:
        #     self.taxid = int(taxid)
        # except ValueError:
        #     err("Taxids must be integers")
        self.sciname = sciname
        self.common_name = common
        self.synonyms = syn

    def add_child(self, child):
        if child:
            self.children.add(child)

    def remove_child(self, child):
        self.children.remove(child)

    def add_taxon(self, taxon):
        if taxon.children:
            for child in taxon.children:
                self.add_taxon(child)
        else:
            path = taxon.get_path()
            self._interweave(path, aligned=bool(path.taxid == self.taxid))

    def get_path(self):
        if not self.parent:
            return(self)
        else:
            self.parent = Taxon.unbranch(self.parent, self)
            return(self.parent.get_path())

    @classmethod
    def unbranch(cls, taxon, child=None):
        ''' gets a taxon with only child '''
        unbranched = Taxon(taxid=taxon.taxid,
                           sciname=taxon.sciname,
                           parent=taxon.parent)
        unbranched.add_child(child)
        return(unbranched)

    def get_root(self):
        ''' Return root Taxon '''
        try:
            return(self.parent.get_root())
        except:
            return(self)

    def print_taxid_lineage(self, lineage=[]):
        ''' Ascend to root collecting taxids, then print all '''
        if self.parent:
            lineage.append(self.taxid)
            self.parent.print_taxid_lineage(lineage)
        else:
            print('; '.join(reversed(lineage)))

    def print_sciname_lineage(self, lineage=[]):
        ''' Ascend to root collecting scinames, then print all '''
        if self.parent:
            lineage.append(self.sciname)
            self.parent.print_sciname_lineage(lineage)
        else:
            print('; '.join(reversed(lineage)))

    def _interweave(self, path, aligned=False):
        ''' Add a linear path to self '''
        # If the out-taxon and self are the same
        if aligned:
            if not (self.children & path.children):
                self.children.update(path.children)
            # Otherwise we descend a level
            elif path.children:
                path = list(path.children)[0]
                for child in self.child:
                    if child.taxid == path.taxid:
                        child._interweave(path, True)
        elif path.parent:
            path = path.parent
            if path.taxid == self.taxid:
                aligned = True
            self._interweave(path, aligned)
        else:
            self = self.get_root()
            self._interweave(path, True)

    def print(self, file=sys.stderr, indent=''):
        # if self.children:
        #     children = ';'.join([str(x.sciname) for x in self.children])
        # else:
        #     children = None
        # parent = self.parent.sciname if self.parent else None
        # selfstr = "{}({},{}) parent='{}' children='{}'".format(
        #           indent, self.taxid, self.sciname, parent, children)
        selfstr = "{}{}".format(indent, self.sciname)
        print(selfstr, file=file)

    def printall(self, file=sys.stderr, indent=''):
        self.print(indent=indent)
        for child in self.children:
            newchar = '|' if (indent and indent[-1] == '.') else '.'
            indent = indent + newchar
            child.printall(indent=indent)

    def __eq__(self, other):
        try:
            return(lambda self, other: int(self.taxid) == int(other.taxid))
        except AttributeError:
            err("Can't compare Taxon object to {}".format(type(other)))
        except ValueError:
            err("Taxids must be integers")

    def __hash__(self):
        try:
            return(int(self.taxid))
        except ValueError:
            err("Taxids must be integers")


def pickle_taxon(taxon, filename):
    # Only pickle if you have a cucumber
    if not taxon.parent and taxon.children:
        with open(filename, 'wb') as f:
                pickle.dump(taxon, f)

def unpickle_taxon(filename):
    try:
        root = pickle.load(open(filename, 'rb'))
    except IOError:
        root = Taxon()
    except Exception as e:
        err('unknown pickle error\n{}'.format(e))
    return(root)
