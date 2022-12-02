import os
import re
import sys
import time
import shutil
import pandas as pd
from app.check_input import check_opts_input, check_opts, check_directories,  count_vcf_files, count_txt_files, count_csv_files, count_xml_files
import app.constants as c
from app.check_modules import check_module
from app.vcf_extraction import pipeline, pipeline_xml, pipeline_vocab, check_hgvs_pattern, check_chr_pattern, pipeline_txt
from app.clingen_parser import parse_clingen
from app.OMOP_mapping import map_to_omop
#import app.move_old_files as move
import psycopg2
from flask import session, render_template



def run_web(filename):
    count_empty_files = 0
    if filename.endswith(".vcf") or filename.endswith(".vcf.gz"):
        path_to_current_file = os.path.join(c.input_dir_path + session["RNDUSERSTR"], filename)
        if os.path.getsize(path_to_current_file) == 0:
            print('file ', filename, ' has 0 characters. Please double check.')
            count_empty_files += 1
            if count_empty_files == 3:
                    return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)

        # CONVERTER
        current_vcf_converted = pipeline(filename)
        time.sleep(2)
        parsed_data = parse_clingen(current_vcf_converted, filename, vcf_mode=True)
        time.sleep(2)

        matches = map_to_omop(parsed_data, filename, vcf_mode=True)


    if filename.endswith(".xml"):
        path_to_current_file = os.path.join(c.input_dir_path + session["RNDUSERSTR"], filename)
        if os.path.getsize(path_to_current_file) == 0:
            print('file ', filename, ' has 0 characters. Please double check.')
            count_empty_files += 1
            if count_empty_files == 3:
                return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)


        # CONVERTER
        current_vcf_converted = pipeline_xml(filename)
        time.sleep(2)
        parsed_data = parse_clingen(current_vcf_converted, filename)
        time.sleep(2)
        map_to_omop(parsed_data, filename)


    if filename.endswith(".txt") or filename.endswith(".csv"):
        path_to_current_file = os.path.join(c.input_dir_path + session["RNDUSERSTR"], filename)
        if os.path.getsize(path_to_current_file) == 0:
            print('file ', filename, ' has 0 characters. Please double check.')
            count_empty_files += 1
            if count_empty_files == 3:
                render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)

        df = pd.read_csv(c.project_dir + '/' + c.input_dir + session["RNDUSERSTR"] + '/' + filename, sep="\t", header=None)

        clean_hgvs_list = check_hgvs_pattern(df)

        try:
            if len(clean_hgvs_list) != 0:

                current_hgvs_generated = pipeline_txt(filename, clean_hgvs_list, 'clean')
                time.sleep(2)
                parsed_data = parse_clingen(current_hgvs_generated, filename, vcf_mode=True, mult_build_mode=False)
                time.sleep(2)
                map_to_omop(parsed_data,filename, vcf_mode=True)

            else:
                chr_hgvs_list = check_chr_pattern(df)
                try:
                    if len(chr_hgvs_list)!=0:

                        current_hgvs_generated = pipeline_txt(filename, chr_hgvs_list, 'chr')
                        time.sleep(2)
                        parsed_data = parse_clingen(current_hgvs_generated, filename, vcf_mode=True, mult_build_mode=True)
                        time.sleep(2)
                        map_to_omop(parsed_data,filename, vcf_mode=True)

                except:
                    return 0


        except:
            chr_hgvs_list = check_chr_pattern(df)
            try:
                if len(chr_hgvs_list)!=0:
                    current_hgvs_generated = pipeline_txt(filename, chr_hgvs_list, 'chr')
                    time.sleep(2)
                    parsed_data = parse_clingen(current_hgvs_generated, filename, vcf_mode=True, mult_build_mode=True)
                    time.sleep(2)
                    map_to_omop(parsed_data,filename, vcf_mode=True)

            except:
                return 0
    print(c.bottom)
