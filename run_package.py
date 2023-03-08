from app.main import main
import app.constants as c
import shutil
import app.move_old_files as move
from app.check_input import check_opts_input, check_opts, check_directories, count_vcf_files, count_txt_files, \
    count_csv_files, count_xml_files

import os
import sys


def config_session():
    shutil.rmtree(c.hgvsg_folder_path)
    shutil.rmtree(c.temp_folder_path)
    hgvs_folder = c.hgvsg_folder_path
    temp_folder = c.temp_folder_path

    os.makedirs(os.path.dirname(c.input_dir_local_path), exist_ok=True)
    os.makedirs(os.path.dirname(c.output_dir_local_path), exist_ok=True)
    os.makedirs(os.path.dirname(temp_folder), exist_ok=True)
    os.makedirs(os.path.dirname(hgvs_folder), exist_ok=True)


def check_file_extension(filename):
    return filename.split('.')[-1] in allowed_extensions


if __name__ == '__main__':
    config_session()

    sys_args = sys.argv[1:]
    opts = check_opts_input(sys_args, c.opts_options_array)
    main_parameters = [opts]
    check_opts(opts, main_parameters)

    main(c.input_dir_local_path, '', website_mode=False)

    if not os.path.exists(c.input_old_path):
        os.mkdir(c.input_old_path)
    if not os.path.exists(c.export_dir_path):
        os.mkdir(c.export_dir_path)

    move.move_old_input_files(c.input_dir_local_path, c.input_old_path)
    move.move_old_input_files(c.output_dir_local_path, c.export_dir_path)
    #shutil.rmtree(c.input_dir_local_path)
    #shutil.rmtree(c.output_dir_local_path)
