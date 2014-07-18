PYB
===

Creates a virtual file directry in which all files are organized by position on
a phylogenetic tree (specifically the NCBI common tree).

Subcommands
===========

 * put - copy files into pyb
 * sput - guess taxon from filename and copy appropriately
 * get - copy files out of pyb
 * ls - list files
 * rm - remove files from the tree
 * mkdir - make a directory rooted at a given node
 * mv - move/rename files
 * rename - a wrapper for UNIX rename command
 * util - various utility functions (updating, diagnostics, BLAST functions, etc)

Examples 
========

(fyi, none of this is yet implemented)

## `pyb put`

Like UNIX `cp` builtin, just substitutes taxon name or id for the
appropriate directory in the local PYBHOME database

```bash
# symlinks files to *Glycine max* (taxid=3847)
# 3847 is the species taxon id
$ pyb put -s Glycine_max.* 3847 
# Or equivalently
$ pyb put -s Glycine_max.* Glycine_max
```

## `pyb sput`

For each file, guesses taxon, then copies (using the builtin `cp`) to that
taxon's directory.

```bash
# let pyb guess the taxa from the filename
$ pyb sput *.{faa,fna}
```

## `pyb get`

Like `pyb put` but copying out of pyb

```bash
# copying from pyb
$ pyb get -s 3847/*faa .
```

## `pyb ls`

Flatly lists files descending from given taxon

```bash
# lists all protein coding sequence files that are in the 'rosids' clade
$ pyb ls rosids/*faa
# list BLAST databases
$ pyb ls -b rosids
# list BLAST CDS databases
$ pyb ls -b rosids/*CDS*
```

## `pyb mkdir`

As with `pyb cp`, just substitutes taxon for path, then uses builtin `mkdir`.

```bash
$ pyb mkdir 3847/ecotypes
$ pyb cp *.faa {3847}/ecotypes
```

## `pyb rm`

```bash
$ pyb rm 3847/ecotypes/*.faa
$ pyb rm 3847/*.faa
# recursively remove everything in this taxon and descending from it
$ pyb rm -rf 3847
```

## `pyb rmdir`

Removes empty directories or taxons (checks recursively to ensure emptiness)

```bash
$ pyb rmdir 3847/ecotypes
$ pyb rmdir 3847
```

## `pyb mv`

```bash
# mv file into a subfolder within pyb
$ pyb mv {3847}/*.faa {3847}/ecotypes
# mv files from outside to pyb
$ pyb mv *.faa {3847}
# mv files out of pyb
$ pyb mv {3847}/*.faa .
```

## `pyb util`

```bash
# remakes tree according to NCBI common tree
$ pyb update
# makes BLAST databases for each protein sequence
$ pyb util --makeblastdb
# remove empty folders
$ pyb util --prune
# list rosids protein blast databases
$ pyb ls -b rosids/*.prot.*
```
