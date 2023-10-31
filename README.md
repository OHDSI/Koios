<!-- README.md is generated from README.Rmd. Please edit that file -->
<p float="left">
<img src="./img/koios.png" style="vertical-align: center;" width="100"/><img src="./img/ods_logo.jpg" style="vertical-align: center;" width="100"/>
</p>

## Overview

KOIOS is a tool developed by [Odysseus Data Services
Inc](https://odysseusinc.com/) that allows users to combine their
variant data with the OMOP Genomic Vocabulary in order to generate a set
of genomic standard concept IDs from raw patient-level genomic data.
KOIOS allows you to extract all relevant variant information from a
given VCF file by automatically finding and parsing the relevant data
found on the \[ClinGen Allele\]
Registry(<https://reg.clinicalgenome.org/redmine/projects/registry/genboree_registry/landing>),
collating all available genomic alleles, as well as any downstream mRNA
or protein variants and finding any corresponding standard concepts
within the OMOP Genomic vocabulary.

## Installation

KOIOS can presently be installed directly from GitHub:

    # install.packages("devtools")
    devtools::install_github("odyOSG/KOIOS")

## Usage

### userScript.R

The file userScript.R may be loaded as a default workflow wherein only
the initial reference genome and VCF file or VCF files directory need be
specified.

### Manual

Users must provide at least one valid VCF file in either .vcf or .vcf.gz
format. This may be in the form of a single file, or a directory
containing a set of .vcf or .vcf.gz files.

Users may simply run KOIOS according to the following simple pipeline:


    library(KOIOS)

    #Load the OMOP Genomic Vocabulary into R
    concepts <- loadConcepts()

    #Specify input file or directort
    vcf <- loadVCF(userVCF = "Input.vcf")

    #Specify and load human reference genome, if known
    ref <- "hg19"
    ref.df <- loadReference(ref)

    #Process VCF and generate all relevant HGVSG identifiers for input records
    vcf.df <- processVCF(vcf)
    vcf.df <- generateHGVSG(vcf = vcf.df, ref = ref.df)

    #Generate all known alleles, including transcript and protein alleles
    alleles.df <- processClinGen(vcf.df,ref,generateAll = generateTranscripts)

    #Combine this output data with the OMOP Genomic vocab to produce output
    concepts.df <- addConcepts(alleles.df, concepts)

If the user is unaware of the reference genome used to generate a given
VCF file, they may use the “automatic” mode found within the
userScript.R file, or alternatively run the following command:

    vcf <- loadVCF(userVCF = "Input VCF")
    ref <- findReference(vcf)
    ref.df <- loadReference(ref)

## Getting help

If you encounter a clear bug, please file an issue with a minimal
[reproducible example](https://reprex.tidyverse.org/) at the [GitHub
issues page](https://github.com/OdyOSG/KOIOS/issues).
