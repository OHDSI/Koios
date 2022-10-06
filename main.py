import os
import re
import sys
import time
import shutil
import pandas as pd
from check_input import check_opts_input, check_opts, check_directories, count_vcf_files
import constants
from check_modules import check_module
from vcf_extraction import pipeline, pipeline_xml, pipeline_vocab
from constants import opts_options_array, input_dir_path
from clingen_parser import parse_clingen
from OMOP_mapping import map_to_omop
import move_old_files
import psycopg2


def main(input_directory,
         opts_options,
         help_param=False, vocab_server=False,
         debug_mode=False, website_mode=False):
    print(constants.heading)
    check_module()

    if debug_mode == False:
        sys_args = sys.argv[1:]
        opts = check_opts_input(sys_args, opts_options)

        main_parameters = [help_param, vocab_server]
        updated_parameters_dict = check_opts(opts, main_parameters)
        vocab_server = updated_parameters_dict

    check_directories(input_directory)
    files_list = os.listdir(input_directory)
    num_files = count_vcf_files(files_list)
    count_empty_files = 0
    print('\nOpening input folder with ... ' + str(num_files) + ' files')
    counter = 0
    time.sleep(2)

    if vocab_server == True:
        print('Internal solution: ')

        conn = psycopg2.connect(database="postgres",
                                host="149.56.241.161",
                                user='pwd',
                                password='usr',
                                port="5555")

        cursor = conn.cursor()

        # query = """SELECT * FROM devv5.concept_synonym cs JOIN devv5.concept c ON c.concept_id = cs.concept_id WHERE c.vocabulary_id IN ('CGI', 'OncoKB', 'CIViC', 'JAX', 'OMOP Genomic')"""

        query = "SELECT * FROM dev_cgi.genomic_cgi_source gen"

        cursor.execute(query)
        records = cursor.fetchall()

        df = pd.DataFrame(records)

        pattern = constants.hgvs_pattern

        hgvs_list = []

        for col in df.columns:
            current_col = df[col]
            count_matches = 0

            for i in range(len(df)):
                test_string = df.at[i, col]
                # print(test_string)

                if re.search(pattern, test_string):
                    count_matches += 1
                    # print(count_matches)

            if count_matches >= 0.7 * len(df):
                hgvs_column_name = col
                print(hgvs_column_name)
                hgvs_list = df[hgvs_column_name]
                break
            else:
                continue

        hgvs_list = df[1]

        print(hgvs_list)
        print(df.head())

        pipeline_vocab(hgvs_list)

    else:
        for current_filename in files_list:
            if current_filename.endswith(".vcf") or current_filename.endswith(".vcf.gz"):
                path_to_current_file = os.path.join(input_dir_path, current_filename)
                if os.path.getsize(path_to_current_file) == 0:
                    print('file ', current_filename, ' has 0 characters. Please double check.')
                    count_empty_files += 1
                    if count_empty_files == 3:
                        sys.exit('At least 3 empty files were found in /input/ folder. '
                                 'Something is wrong\n' + constants.bottom)
                    continue

                # CONVERTER
                current_vcf_converted = pipeline(current_filename)
                time.sleep(2)
                parsed_data = parse_clingen(current_vcf_converted, current_filename, vcf_mode=True)
                time.sleep(2)

                matches = map_to_omop(parsed_data, current_filename, vcf_mode=True)

            if current_filename.endswith(".xml"):
                path_to_current_file = os.path.join(input_dir_path, current_filename)
                if os.path.getsize(path_to_current_file) == 0:
                    print('file ', current_filename, ' has 0 characters. Please double check.')
                    count_empty_files += 1
                    if count_empty_files == 3:
                        sys.exit('At least 3 empty files were found in /input/ folder. '
                                 'Something is wrong\n' + constants.bottom)
                    continue

                # CONVERTER
                current_vcf_converted = pipeline_xml(current_filename)
                time.sleep(2)
                parsed_data = parse_clingen(current_vcf_converted, current_filename)
                time.sleep(2)
                map_to_omop(parsed_data, current_filename)
                counter += 1

            if counter == num_files:
                move_old_files.move_old_input_files(input_dir_path, constants.input_old_path)
                shutil.rmtree(constants.hgvsg_folder_path)
                shutil.rmtree(constants.temp_folder_path)
                print(constants.bottom)


if __name__ == '__main__':
    main(input_directory=input_dir_path, opts_options=opts_options_array,
         help_param=False, vocab_server=True, debug_mode=True, website_mode=False)

# %%
