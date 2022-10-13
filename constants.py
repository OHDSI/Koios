import os


assembly_dir = 'assembly_files/'
input_dir = 'input/'
output_dir = 'output/'
export_dir = 'output_archive/'
temp_folder = 'temp/'
hgvsg_folder = 'hgvsg/'
input_old = 'input_archive/'
vocab = 'OMOP_Genomic/'

project_dir = os.path.dirname(os.path.abspath('main.py'))
input_dir_path = os.path.join(project_dir, input_dir)
output_dir_path = os.path.join(project_dir, output_dir)
temp_folder_path = os.path.join(project_dir, temp_folder)
hgvsg_folder_path = os.path.join(project_dir, hgvsg_folder)
assembly_dir_path = os.path.join(project_dir, assembly_dir)
input_old_path = os.path.join(project_dir, input_old)
vocab_path = os.path.join(project_dir, vocab)

os.makedirs(os.path.dirname(input_old_path), exist_ok=True)
os.makedirs(os.path.dirname(output_dir_path), exist_ok=True)
os.makedirs(os.path.dirname(temp_folder_path), exist_ok=True)
os.makedirs(os.path.dirname(hgvsg_folder_path), exist_ok=True)
os.makedirs(os.path.dirname(assembly_dir_path), exist_ok=True)
os.makedirs(os.path.dirname(input_dir_path), exist_ok=True)
os.makedirs(os.path.dirname(vocab_path), exist_ok=True)



# terminal parameters options
opts_options_array = ['--vocab_server', '-vs',
                      '--help', '-h']

# terminal messages
heading = ('\n' + f"{'=================================================================':>65}" +
           '\n' + f"{'Welcome to VCF-to-OMOP -> Odysseus VCF to OMOP Mapper 1.0.': ^65}" +
           '\n\nPython script that converts data from VCF files to HGVSg represen' +
           '\ntations, extracts matching references from ClinGen, and maps them' +
           '\nto OMOP Genomic vocabulary' +
           '\n' + f"{'=================================================================':>65}")

to_begin = ('\nTo begin using this converter, put VCF files (in .vcf / .vcf.gz' +
            '\nformats) to /omopvcf/input/ directory.\n')

default_converter_steps = ('\nDefault converter steps:' +
                           '\n' + f"{'    1) Extract variants data from a VCF file. Create': <50}" +
                           '\n' + f"{'       HGVSg representations.': <50}" +
                           '\n' + f"{'       ---------------------------------------------------':<50}" +
                           '\n' + f"{'    2) Parse ClinGen and find all hgvs references': <50}" +
                           '\n' + f"{'       matching these HGVSg representations.': <50}" +
                           '\n' + f"{'       ---------------------------------------------------':<50}" +
                           '\n' + f"{'    3) Map extracted hgvs to OMOP Genomic, field': <50}" +
                           '\n' + f"{'       concept_synonym_name.': <50}" +
                           '\n' + f"{'       ---------------------------------------------------':<50}" +
                           '\n' + f"{'    -  move current /input/ files to /old_input_files/.': <50}")

syntax = ('\n\nSyntax:' +
          '\n' + f"{'     ': <5}{'python main.py [-h | -cl ][--help | --clingen]': <43}" +
          '\n' + f"{'     f.e.   python3 main.py': <25}" +
          '\n' + f"{'            python3 main.py -h': <25}" +
          '\n\n')

bottom = ('\n' + f"{'=================================================================':>65}" +
          '\n' + f"{'Use README.txt file for more information.':^65}" +
          '\n' + f"{'Thank you for using this mapper.':^65}" +
          '\n' + f"{'Odysseus Data Sevices': >65}" +
          '\n' + f"{'nadia.kadakova@odysseusinc.com': >65}" +
          '\n' + f"{'=================================================================':>65}")

split_line = '\n' + f"{'=================================================================':>65}"

split_line_thin = '\n' + f"{'---------------':<65}"

starting_line = '\n' + f"{'Starting mapper...':^65}"

chr_hgvs_pattern = "chr\w+\:g.\d+.+"

clean_pattern = "NC_\d+\.\d+\:g.\d+.+"