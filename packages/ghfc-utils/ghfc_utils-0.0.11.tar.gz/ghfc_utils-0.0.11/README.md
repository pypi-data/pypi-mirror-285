# ghfc-utils

set of small tools designed to help automatize simple task locally or on Pasteur's cluster.

- **ghfc-reannotate** for the postprocessing of slivar files including filtering and geneset reannotation.

## Installation

```
pip install ghfc-utils
```

PS. on maestro, do not forget to load Python first (not needed anymore once installed):
```
module load Python/3.9.16
```

## slivar reannotator

A tool to filter and reannotate slivar files according to various parameters and genesets. The goal is to produce a more generic kind of slivar files and to use this for the user to run their own filtering.
*ghfc-reannotate* reads a slivar file and given a config file, will return an annotated and filtered slivar file.

```
usage: ghfc-reannotate [-h] [-c CHUNKSIZE] [-k] [-p] [-v] configuration slivar output

A tool to filter and reannotate slivar files according to various parameters and genesets.

positional arguments:
  configuration         config file
  slivar                slivar file to reannotate
  output                annotated slivar file

optional arguments:
  -h, --help            show this help message and exit
  -c CHUNKSIZE, --chunksize CHUNKSIZE
                        size of the chunks read from the input (default 100000)
  -k, --keep-all-transcripts
                        to keep all impacted transcript instead of the first
  -p, --progress        display a progress bar
  -v, --verbose         activate verbose mode
```

### Example

You need to prepare a config file or take the one provided [here](https://gitlab.pasteur.fr/ghfc/ghfc-utils/-/blob/master/test/configurations/HC-NDD.dom.v5.lof.yaml).
Then, you need a slivar file to run the tool on. For instance you can use the 570MB file at */pasteur/zeus/projets/p02/ghfc_wgs_zeus/WGS/Paris-AIMS2/slivar/Paris-AIMS2.slivar-full.lof_miss.tsv* on zeus. 

```
ghfc-reannotate config.yaml input_slivar.tsv output_slivar.tsv
```

The provided config file has a lot of comments to help build a new one.

### how is it working?

- This tools read the slivar file before decomposing the impacts by transcripts (so 1 line per trancsript). 
    - as slivar files can be really large in some project, the reading is done by chunks of 100k rows.
- Then filters on samples if required
- Then, it filters all lines using, in this order following the config file parameters:
    1. the geneset (based on the ENSG, mind the GRCh37/GRCh38 differences in ENSG)
    2. the impact / impact-categories
    3. if missense are kept, filtering them on their impact (using scores such as the mpc or the cadd)
    4. the gnomad frequency
    5. the pext
    6. LCR
- the variant/transcript are then sorted according to criteria given by the user in the config file from the most important to the least important
- for each sample, variant and gene (ENSG) the first transcript (most important given by the config criteria) is kept unless the *--keep-all-transcripts* option is used.

### pext file

The pext is a bed file with the following columns (order important, there must be some header):
```
chr	start	end	max_brain	ensg	symbol
```
Need to have the genome version to match the data (GRCh37/38 and using the chr or not in the chromosome names)
