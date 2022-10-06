
=================================================================
    Welcome to VCF-to-OMOP -> Odysseus VCF to OMOP Mapper 1.0.

Python package that converts data from VCF files to HGVSg represe
ntations, extracts matching references from ClinGen and maps them
to OMOP Genomic vocabulary.
=================================================================
This package is written completely in Python 3, so you need it to 
be installed on your computer.
The package also requires 'pandas' and 'requests' Python modules:

    pip install pandas
    pip install requests

OR

    pip install -r requirements.txt

(Run in terminal or command prompt)

-----------------------------------------------------------------
                    MANUAL - Installation
-----------------------------------------------------------------
I. Download all files and folders as a .zip archive from:

	https://github.com/NadzeyaKadakova/omopvcf (private)

II. Move 'omopvcf.zip' archive to your desired directory and
unzip it.

-----------------------------------------------------------------
                  MANUAL - Run the converter
-----------------------------------------------------------------
III. Put VCF files to /omopvcf/input/ directory.

    Supported input file formats:
    - .vcf
    - .vcf.gz

IV. Run main.py file (in terminal or command prompt)

Syntax:
1)	cd ../full_path_to_folder/../omopvcf/

2) 	python3 main.py [-h ][--help ]

	f.e.   python3 main.py -h 
	       python3 main.py --help


Options for running main.py:

     Parameter   Default usage           Description

     ------------------------------------------------------------
    --help  -h    False      Display (this) help message.

-----------------------------------------------------------------
                    DEFAULT CONVERTER STEPS
-----------------------------------------------------------------
After you start running the converter in default mode, the next
steps will be executed:

-----------------------------------------------------------------
                     STEP 1: VCF PROCESSING
-----------------------------------------------------------------
    1.1) Parse a VCF file and extract variants data. A VCF file 
contains the variants of a single patient.

-----------------------------------------------------------------
    1.2) Create HGVSg representations. Important: Currently, the 
converter only works for Substitution and Deletion (VTYPE=='snv',
'del') 

Format: 
	Reference : Description

Steps: 
	- Extract Build and Chromosome Number (tag CHROM in the 
VCF file). Map this information to Global Assembly Definitions [1] 
provided by Genome Reference Consortium to find Reference Sequence 
Accession Number. 
	Example: 'NC_000001.11' for Chromosome 1 and Build 38
	
	- Extract position (tag POS in the VCF file)
	Example: 114713909
 
	- Extract the reference genotype (tag REF in the VCF file) 
	- Extract the alleles that differ from the reference 
	read (tag ALT in the VCF file)
	Transformation is coded as: REF>ALT, f.e. G>T
	
	Result: NC_000001.11:g.114713909G>T

-----------------------------------------------------------------
                    STEP 2: CLINGEN PARSER
-----------------------------------------------------------------
    2.1) Generate ClinGen links based on HGVSg formed in the pre
vious step. 

	Example link: [2]

-----------------------------------------------------------------
    2.2) Parse all available HGVS references matching the HGVSg 
representations. 

    File format:

    VCF_file_name_clingen.csv

Columns: 
	HGVSg_vcf: 		HGVSg formed at step 1.2)
	link: 			linked to ClinGen API formed at step 2.1)
	communityStandardTitle: 	Clingen communityStandardTitle tag
	allele_class: 		r.n. only data about genomicAlleles is extracted
	type: 			Clingen type tag
	chromosome: 		Clingen chromosome tag. Chromosome number of each allele
	allele_n: 		Number of allele 
	hgvs: 			Clingen hgvs tag. HGVS reference
	hgvs_n: 			Number of HGVS reference
	hgvs_referenceGenome: 	Clingen referenceGenome tag
	referenceSequence: 	Clingen referenceSequence tag
	hgvs_referenceSequence: 	Clingen referenceSequence tag

-----------------------------------------------------------------
                 STEP 3: OMOP MAPPING
-----------------------------------------------------------------
    3.1) Map extracted hgvs to OMOP Genomic vocabulary, table 
CONCEPT SYNONYMS, field concept_synonym_name. Display matches

    3.2) Save matching hgvs as a .csv file. Output file location:

- /omopvsf/output


=================================================================

               Thank you for using this converter.
                                            Odysseus Data Sevices
				 nadia.kadakova@odysseusinc.com
=================================================================


Links
[1] https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.26/
[2] reg.genome.network/allele?hgvs=NC_000001.11:g.114713909G>T



