import os
import re
import sys
import time
import shutil
import pandas as pd
from check_input import check_opts_input, check_opts, check_directories,  count_vcf_files, count_txt_files, count_csv_files, count_xml_files
import constants
from check_modules import check_module
from vcf_extraction import pipeline, pipeline_xml, pipeline_vocab, check_hgvs_pattern, check_chr_pattern, pipeline_txt
from constants import opts_options_array, input_dir_path
from clingen_parser import parse_clingen
from OMOP_mapping import map_to_omop
import move_old_files
import psycopg2
from flask import render_template


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
    num_vcf_files = count_vcf_files(files_list)
    num_xml_files = count_xml_files(files_list)
    num_txt_files = count_txt_files(files_list)
    num_csv_files = count_csv_files(files_list)

    count_empty_files = 0
    print('\nOpening input folder with ... :\n\t' + str(num_vcf_files) + ' VCF files,' +
          '\n\t' + str(num_xml_files) + ' XML files' +
          '\n\t' + str(num_txt_files) + ' TXT files' +
          '\n\t' + str(num_csv_files) + ' CSV files')

    counter = 0
    num_files = num_vcf_files + num_xml_files + num_txt_files + num_csv_files
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

                hgvs_list = df[hgvs_column_name]
                break
            else:
                continue

        hgvs_list = df[1]


        pipeline_vocab(hgvs_list)

    else:
        for current_filename in files_list:
            if current_filename.endswith(".vcf") or current_filename.endswith(".vcf.gz"):
                path_to_current_file = os.path.join(input_dir_path, current_filename)
                if os.path.getsize(path_to_current_file) == 0:
                    print('file ', current_filename, ' has 0 characters. Please double check.')
                    count_empty_files += 1
                    if count_empty_files == 3:
                        if not website_mode:

                            sys.exit('At least 3 empty files were found in /input/ folder. '
                                 'Something is wrong\n' + constants.bottom)
                        else:
                            return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)
                    continue

                # CONVERTER
                current_vcf_converted = pipeline(current_filename)
                time.sleep(2)
                parsed_data = parse_clingen(current_vcf_converted, current_filename, vcf_mode=True)
                time.sleep(2)
                matches = map_to_omop(parsed_data, current_filename, vcf_mode=True)
                counter += 1

            if current_filename.endswith(".xml"):
                path_to_current_file = os.path.join(input_dir_path, current_filename)
                if os.path.getsize(path_to_current_file) == 0:
                    print('file ', current_filename, ' has 0 characters. Please double check.')
                    count_empty_files += 1
                    if count_empty_files == 3:
                        if not website_mode:
                            sys.exit('At least 3 empty files were found in /input/ folder. '
                                 'Something is wrong\n' + constants.bottom)
                        else:
                            return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)
                    continue

                # CONVERTER
                current_vcf_converted = pipeline_xml(current_filename)
                time.sleep(2)
                parsed_data = parse_clingen(current_vcf_converted, current_filename)
                time.sleep(2)
                map_to_omop(parsed_data, current_filename)
                counter += 1

            if current_filename.endswith(".txt") or current_filename.endswith(".csv"):
                path_to_current_file = os.path.join(input_dir_path, current_filename)
                if os.path.getsize(path_to_current_file) == 0:
                    print('file ', current_filename, ' has 0 characters. Please double check.')
                    count_empty_files += 1
                    if count_empty_files == 3:
                        if not website_mode:
                            sys.exit('At least 3 empty files were found in /input/ folder. '
                                 'Something is wrong\n' + constants.bottom)
                        return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)
                    continue

                df = pd.read_csv(constants.project_dir + '/' + constants.input_dir + current_filename, sep="\t", header=None)

                clean_hgvs_list = check_hgvs_pattern(df)

                try:
                    if len(clean_hgvs_list) != 0:

                        current_hgvs_generated = pipeline_txt(current_filename, clean_hgvs_list, 'clean')
                        time.sleep(2)
                        parsed_data = parse_clingen(current_hgvs_generated, current_filename, vcf_mode=True, mult_build_mode=False)
                        time.sleep(2)
                        map_to_omop(parsed_data,current_filename, vcf_mode=True)

                    else:
                        chr_hgvs_list = check_chr_pattern(df)
                        try:
                            if len(chr_hgvs_list)!=0:

                                current_hgvs_generated = pipeline_txt(current_filename, chr_hgvs_list, 'chr')
                                time.sleep(2)
                                parsed_data = parse_clingen(current_hgvs_generated, current_filename, vcf_mode=True, mult_build_mode=True)
                                time.sleep(2)
                                map_to_omop(parsed_data,current_filename, vcf_mode=True)

                        except:
                            if not website_mode:

                                sys.exit('The input file ' + current_filename + 'doesn\'t contain columns with HGVS. \n'
                                                                                'Please try again\n' + constants.bottom)
                            else:
                                return 0
                    counter += 1

                except:
                    chr_hgvs_list = check_chr_pattern(df)
                    try:
                        if len(chr_hgvs_list)!=0:
                            current_hgvs_generated = pipeline_txt(current_filename, chr_hgvs_list, 'chr')
                            time.sleep(2)
                            parsed_data = parse_clingen(current_hgvs_generated, current_filename, vcf_mode=True, mult_build_mode=True)
                            time.sleep(2)
                            map_to_omop(parsed_data,current_filename, vcf_mode=True)
                            counter += 1

                    except:
                        if not website_mode:
                            counter += 1
                            sys.exit('The input file ' + current_filename + 'doesn\'t contain columns with HGVS. \n'
                                                                            'Please try again\n' + constants.bottom)
                        else:
                            return 0


            #if counter == num_files:
            move_old_files.move_old_input_files(input_dir_path, constants.input_old_path)
            #shutil.rmtree(constants.hgvsg_folder_path)
            #shutil.rmtree(constants.temp_folder_path)
            print(constants.bottom)


if __name__ == '__main__':
    main(input_directory=input_dir_path, opts_options=opts_options_array,
         help_param=False, vocab_server=True, debug_mode=True, website_mode=False)

# %%
