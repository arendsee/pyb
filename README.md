PYB
===

Description
===========

Creates a virtual file directry in which all files are organized by position on
a phylogenetic tree (specifically the NCBI common tree).

Subcommands
===========

 * add - add a new file to the tree
 * rm - remove a file from the tree
 * ls - list files
 * cp - copy from the tree to filesystem
 * util - various utility functions (updating, diagnostics, BLAST functions, etc)

Examples 
========

(fyi, none of this is yet implemented)

## pyb add - add files to the virtual directory

``` bash
# Adds a file containing *Glycine max* protein sequence
# 3847 is the species taxon id
$ pyb add -q prot -f Glycine_max.faa -d 3847 
# Or equivalently
$ pyb add -q prot -f Glycine_max.faa -d 'Glycine_max'
# Or let pyb guess the taxon and sequence type from the filename
$ pyb add -gf Glycine_max.faa
```

## `pyb ls` - list files in the virtual directory

```bash
# Lists all protein coding sequence files that are in the 'rosids' clade
$ pyb ls -q prot -d rosids
# Lists as space delimited (e.g. as arguments to other programs)
$ pyb ls -q prot -d rosids -s
```

## `pyb cp` - copies data to given directory

```bash
# copies data
$ pyb cp -q nucl gff -d rosids $HOME/path/to/wherever
# symlinks data rather than copying
$ pyb cp -s -q nucl gff -d rosids $HOME/path/to/wherever
# hard links data rather than copying
$ pyb cp -l -q nucl gff -d rosids $HOME/path/to/wherever
```

## `pyb util` - utilities

```bash
# Makes BLAST databases for each protein sequence
$ pyb util --makeblastdb
# To make a blastdb of rosids protein sequences
$ blastdb_aliastool -dbtyp prot -title rosids -out rosids \
$ -dblist `pyb ls -s -d rosids -b prot`
```


