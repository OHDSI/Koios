import sys
import app.constants as c
import os


def check_opts_input(opts_input, opts_options):
    opts_checked = []
    for opt in opts_input:
        if opt.startswith("-") and opt in opts_options:
            opts_checked.append(opt)
        else:
            print(f'Warning: Wrong function parameter {opt}. Please try again without '
                  f'{opt} or run \'python main.py -h\' for help.\n')
            sys.exit(c.bottom)

    return opts_checked


def check_opts(opts_array, parameters_array):
    help_param, vocab_server = parameters_array

    # Help
    if '-h' in opts_array or '--help' in opts_array or help_param:
        print(c.to_begin,
              c.default_converter_steps,
              c.syntax, c.bottom)
        if len(opts_array) != 1:
            sys.exit('\nWarning: Run program without -h / --help parameter '
                     'to use the converter.\n')
        sys.exit()

    # Default
    if len(opts_array) == 0:

        print('You\'re using VCF-to-OMOP mapper in the default mode. '
              'Next steps\nwill be executed:')
        print(c.default_converter_steps)

    if '-vs' in opts_array or '--vocab_server' in opts_array or vocab_server:
        no_move = True
        print('Warning: You selected --vocab_server mode.')
        user_answer = input('Do you want to continue? (y/n)\n')
        if user_answer == 'y' or user_answer == 'y ' or user_answer.startswith('ye'):
            print('ok.')
        elif user_answer == 'n' or user_answer.startswith('no'):
            sys.exit('\nPlease, run '
                     'the converter again\nwith no parameters.\n' + c.bottom)
        else:
            sys.exit('Wrong user input.\n\n'
                     '  - If you want to use vocab_server mode, please,\n'
                     'run the converter again with parameters -vs or --vocab_server\n\n'
                     + c.bottom)
        vocab_server=True

    return vocab_server


def check_directories(input_dir):
    input_files = os.listdir(input_dir)
    if not any(os.scandir(input_dir)) \
            or (len(input_files) == 1 and input_files[0].endswith('.DS_Store')):

        sys.exit('\nWarning: /input/ directory is empty. Please add input files.\n'
                     + c.bottom)


def count_vcf_files(filenames_array):
    num_vcf_files = 0
    for file in filenames_array:
        if '.vcf' in file:
            num_vcf_files += 1
    return num_vcf_files


def count_txt_files(filenames_array):
    num_txt_files = 0
    for file in filenames_array:
        if '.txt' in file:
            num_txt_files += 1
    return num_txt_files


def count_csv_files(filenames_array):
    num_csv_files = 0
    for file in filenames_array:
        if '.csv' in file:
            num_csv_files += 1
    return num_csv_files


def count_xml_files(filenames_array):
    num_xml_files = 0
    for file in filenames_array:
        if '.xml' in file:
            num_xml_files += 1
    return num_xml_files