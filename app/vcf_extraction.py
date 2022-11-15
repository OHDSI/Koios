import gzip
import os
import pandas as pd
import numpy as np
import app.constants as c
import requests
import xmltodict
import re
import csv


def get_chr_names(vcf_path):
    with open(vcf_path, "rt") as ifile:
        for line in ifile:
            if line.startswith("# Sequence-Name"):
                vcf_names = [x for x in line.split('\t')]
                break
    ifile.close()
    return vcf_names


def get_vcf_names(vcf_path):
    if vcf_path.endswith(".vcf.gz"):
        with gzip.open(vcf_path, "rt") as ifile:
            for line in ifile:
                if line.startswith("#CHROM"):
                    vcf_names = [x for x in line.split('\t')]
                    return vcf_names
        ifile.close()

    if vcf_path.endswith(".vcf"):
        with open(vcf_path, "rt") as ifile:
            for line in ifile:
                if line.startswith("#CHROM"):
                    vcf_names = [x for x in line.split('\t')]
                    return vcf_names
    else:
        vcf_names = 'wrong'  # id files like .DS_Store are present in the directory
        return vcf_names


def create_build_file(build_file_path):
    chr_names = get_chr_names(build_file_path)
    chr_coding = pd.read_csv(build_file_path,
                             comment='#', iterator=True, chunksize=1000, delim_whitespace=True, header=None,
                             names=chr_names, nrows=24)
    for chunk in chr_coding:
        chunk.to_csv(build_file_path + 'chr-coding.csv', sep=',', index=False, header=chr_names)

    build_file = pd.read_csv(build_file_path + 'chr-coding.csv', sep=',')
    build_file = build_file[['Sequence-Role', 'Relationship']]
    return build_file


def pipeline_xml(filename_xml):
    url = 'http://reg.test.genome.network/allele?hgvs='

    build_file = create_build_file(c.assembly_dir_path + 'GCF_000001405.26_GRCh38_assembly_report.txt')
    build_file2 = create_build_file(c.assembly_dir_path + 'GCF_000001405.13_GRCh37_assembly_report.txt')

    with open(filename_xml, 'r') as f:
        data = f.read()
    dict_data = xmltodict.parse(data)
    variants_data = dict_data['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['short-variants'][
        'short-variant']
    count_snv = 0
    count_ins = 0
    count_dele = 0

    result = []

    for i in range(len(variants_data)):
        position = variants_data[i]['@position']
        parse_position = re.findall('\d+', position)
        transform = variants_data[i]['@cds-effect']
        chrom = parse_position[0]
        pos = parse_position[1]
        build_ref_1 = build_file[build_file['Sequence-Role'] == chrom].reset_index()['Relationship'][0]
        build_ref_2 = build_file2[build_file2['Sequence-Role'] == chrom].reset_index()['Relationship'][0]

        snv = re.findall('(\D>\D)', transform)
        if len(snv) != 0:
            count_snv += 1
            snv = snv[0]
            hgvs = str(build_ref_1) + ':g.' + str(pos) + str(snv)
            hgvs2 = str(build_ref_2) + ':g.' + str(pos) + str(snv)
            url1 = url + hgvs
            url2 = url + hgvs2
            result.append([chrom, pos, snv, build_ref_1, build_ref_2, hgvs, hgvs2, url1, url2, ''])
            continue

        ins = re.findall('ins(\D+)', transform)
        if len(ins) != 0:
            count_ins += 1
            ins = ins[0]
            hgvs = str(build_ref_1) + ':g.' + str(int(pos) - len(ins)) + 'ins' + str(ins)
            hgvs2 = str(build_ref_2) + ':g.' + str(int(pos) - len(ins)) + 'ins' + str(ins)
            url1 = url + hgvs
            url2 = url + hgvs2
            result.append([chrom, pos, 'ins' + str(ins), build_ref_1, build_ref_2, hgvs, hgvs2, url1, url2, ''])
            continue

        dele = re.findall('del(\D+)', transform)
        if len(dele) != 0:
            count_dele += 1
            dele = dele[0]
            hgvs = str(build_ref_1) + ':g.' + str(int(pos) + len(dele)) + 'del' + str(dele)
            hgvs2 = str(build_ref_1) + ':g.' + str(int(pos) + len(dele)) + 'del' + str(dele)
            url1 = url + hgvs
            url2 = url + hgvs2
            result.append([chrom, pos, 'del' + str(dele), build_ref_1, build_ref_2, hgvs, hgvs2, url1, url2, ''])
            continue

    results = pd.DataFrame(result,
                           columns=['#CHROM', 'POS', 'transform', 'refseq_38', 'refseq_37', 'HGVSg', 'HGVSg37', 'url38',
                                    'url37', 'message'])

    print('Length: ', len(variants_data), '   # of SNV types: ', count_snv,
          '   # of DEL types: ', count_dele,
          '   # of INS types: ', count_ins)

    results.to_csv(c.hgvsg_folder_path + filename_xml + '_hgvsg' + '.csv', index=False, sep='\t')

    return results


def pipeline(filename_vcf_gz):
    build_file = create_build_file(c.assembly_dir_path + 'GCF_000001405.26_GRCh38_assembly_report.txt')
    build_file2 = create_build_file(c.assembly_dir_path + 'GCF_000001405.13_GRCh37_assembly_report.txt')

    print('\nProcessing file: ' + filename_vcf_gz)
    filename_vcf_gz_path = c.project_dir + '/' + c.input_dir + filename_vcf_gz

    names = get_vcf_names(filename_vcf_gz_path)
    if names == 'wrong':
        print('skipped, wrong format')
        return 'wrong'

    if filename_vcf_gz.endswith(".vcf.gz"):
        vcf = pd.read_csv(filename_vcf_gz_path,
                          compression='gzip', comment='#', iterator=True, chunksize=10000, delim_whitespace=True,
                          header=None, names=names)

    else:
        vcf = pd.read_csv(filename_vcf_gz_path,
                          comment='#', iterator=True, chunksize=10000, delim_whitespace=True,
                          header=None, names=names)

    for chunk in vcf:
        chunk.to_csv(c.temp_folder + 'vcf_sample.csv', sep=',', index=False, header=names)

    vcf_current = pd.read_csv(c.temp_folder + 'vcf_sample.csv', sep=',')

    np.warnings.filterwarnings('ignore')

    vcf_current['variation'] = vcf_current['INFO'].str.findall(r'VTYPE=(\w+);').str[0]
    vcf_current['variation_long'] = vcf_current['INFO'].str.findall(r'VARDICT_TYPE=(\w+);').str[0]
    vcf_current['chrom_n'] = vcf_current['#CHROM'].str.slice(start=3)

    result_vcf = vcf_current.merge(build_file, left_on='chrom_n', right_on='Sequence-Role')
    result_vcf = result_vcf.loc[result_vcf['variation'].isin(['snv', 'del', 'ins'])]
    result_vcf['message'] = ''

    snv_vcf = result_vcf[result_vcf['variation'] == 'snv']
    del_vcf = result_vcf[result_vcf['variation'] == 'del']
    ins_vcf = result_vcf[result_vcf['variation'] == 'ins']

    del_ins_vcf = del_vcf[del_vcf['variation_long'] == 'Complex']
    ins_del_ins_vcf = ins_vcf[ins_vcf['variation_long'] == 'Complex']
    del_noins_vcf = del_vcf[del_vcf['variation_long'] != 'Complex']
    ins_nodel_vcf = ins_vcf[ins_vcf['variation_long'] != 'Complex']

    print('Length: ', len(vcf_current), '   # of SNV types: ', len(snv_vcf),
          '   # of DEL types: ', len(del_noins_vcf), '\n# of DELINS types: ', len(del_ins_vcf) + len(ins_del_ins_vcf),
          '   # of INS types: ', len(ins_nodel_vcf))

    snv_vcf['HGVSg'] = snv_vcf['Relationship'] + ':g.' + snv_vcf['POS'].astype('str') + snv_vcf[
        'REF'] + '>' + snv_vcf['ALT']

    # print(len(snv_vcf), ' SNVs processed')

    del_vcf['len_deletion'] = del_vcf['REF'].str.len() - 1
    del_vcf['len_left_part'] = del_vcf['ALT'].str.len()
    del_vcf.astype({"len_deletion": "int32",
                    "len_left_part": "int32",
                    "POS": "int32"})

    del_vcf['start_deletion'] = del_vcf['POS'] + del_vcf['len_left_part']
    del_vcf['end_deletion'] = del_vcf['POS'] + del_vcf['len_deletion']
    del_vcf['end_deletion'] = '_' + del_vcf['end_deletion'].astype(str)
    del_vcf['left'] = del_vcf.apply(lambda x: x['REF'][:x['len_left_part']], 1)
    del_vcf['deleted'] = del_vcf.apply(lambda x: x['REF'][x['len_left_part']:], 1)
    del_vcf.loc[(del_vcf['left'] == del_vcf['ALT']) & (del_vcf['len_deletion'] == 1), 'end_deletion'] = ''
    # print(del_vcf.loc[del_vcf['left'] == del_vcf['ALT']].head(5))

    del_vcf['HGVSg'] = del_vcf['Relationship'] + ':g.' + del_vcf['start_deletion'].astype(str) + \
                       del_vcf['end_deletion'].astype(str) + 'del' + del_vcf['deleted'].astype(str)

    del_vcf.loc[del_vcf['left'] != del_vcf['ALT'], 'message'] = 'check'
    del_vcf.loc[del_vcf['left'] != del_vcf['ALT'], 'HGVSg'] = del_vcf['Relationship'] + ':g.' + (del_vcf['POS']).astype(
        str) + \
                                                              del_vcf['end_deletion'].astype(str) + 'del' + del_vcf[
                                                                  'REF'].astype(str) + 'ins' + del_vcf['ALT'].astype(
        str)

    ins_vcf['len_base'] = ins_vcf['REF'].str.len()
    ins_vcf['len_ins'] = ins_vcf['ALT'].str.len() - 1

    ins_vcf.astype({"len_base": "int32",
                    "POS": "int32"})
    ins_vcf['end_position'] = ins_vcf['POS'] + 1
    ins_vcf['end_position'] = '_' + ins_vcf['end_position'].astype(str)
    ins_vcf['end_delins'] = ins_vcf['POS'] + ins_vcf['len_base'] - 1
    ins_vcf['end_delins'] = '_' + ins_vcf['end_delins'].astype(str)

    ins_vcf['alt_old'] = ins_vcf.apply(lambda x: x['ALT'][:x['len_base']], 1)
    ins_vcf['alt_inserted'] = ins_vcf.apply(lambda x: x['ALT'][x['len_base']:], 1)

    ins_vcf.loc[(ins_vcf['len_base'] == 1), 'end_delins'] = ''

    ins_vcf['HGVSg'] = ins_vcf['Relationship'] + ':g.' + ins_vcf['POS'].astype(str) + \
                       ins_vcf['end_position'].astype(str) + 'ins' + ins_vcf['alt_inserted'].astype(str)
    ins_vcf.loc[ins_vcf['alt_old'] != ins_vcf['REF'], 'message'] = 'check'
    ins_vcf.loc[ins_vcf['alt_old'] != ins_vcf['REF'], 'HGVSg'] = ins_vcf['Relationship'] + ':g.' + (
    ins_vcf['POS']).astype(str) + \
                                                                 ins_vcf['end_delins'].astype(str) + 'del' + ins_vcf[
                                                                     'REF'].astype(str) + 'ins' + ins_vcf['ALT'].astype(
        str)

    columns = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'variation', 'chrom_n', 'Relationship', 'HGVSg', 'message']
    del_vcf = del_vcf[columns]
    snv_vcf = snv_vcf[columns]
    ins_vcf = ins_vcf[columns]

    final_vcf = pd.concat([snv_vcf, del_vcf, ins_vcf], axis=0)

    url = 'http://reg.test.genome.network/allele?hgvs='
    final_vcf['url'] = url + final_vcf['HGVSg']

    # final_vcf.to_csv(hgvsg_folder_path + filename_vcf_gz + '_hgvsg' + '.csv', index=False, sep='\t')

    final_vcf.to_csv(c.hgvsg_folder_path + 'outputHGVSg.csv', index=False, sep='\t')

    print('\nHGVSg are extracted and temporarily saved at /hgvsg/')
    return final_vcf


def pipeline_txt(filename, hgvs_list, mode='clean'):

    build_file = create_build_file(c.assembly_dir_path + 'GCF_000001405.26_GRCh38_assembly_report.txt')
    build_file2 = create_build_file(c.assembly_dir_path + 'GCF_000001405.13_GRCh37_assembly_report.txt')

    url = 'http://reg.test.genome.network/allele?hgvs='

    if mode == 'clean':
        final_hgvs = pd.DataFrame()
        final_hgvs['HGVSg'] = hgvs_list
        final_hgvs['url'] = url + final_hgvs['HGVSg'].astype(str)
        final_hgvs.to_csv(c.hgvsg_folder_path + 'outputHGVSg.csv', index=False, sep='\t')
        return final_hgvs

    if mode == 'chr':
        hgvs_file_name = c.hgvsg_folder_path + 'outputHGVSg.csv'
        with open(hgvs_file_name, 'w', encoding='utf-8') as csvfile:

            fieldnames = ['HGVSg', 'HGVSg37', 'url', 'url37']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()

            num_hgvs = len(hgvs_list)
            for i in range(num_hgvs):
                hgvs = hgvs_list[i]

                chr_num = re.findall(r'chr(\w)', hgvs)[0]

                rel_code_38 = build_file[build_file['Sequence-Role']==chr_num].reset_index()['Relationship'][0]

                rel_code_37 = build_file2[build_file2['Sequence-Role']==chr_num].reset_index()['Relationship'][0]

                right_part = re.findall(r'chr\w(.+)',hgvs)[0]
                hgvs_38 = rel_code_38 + right_part
                hgvs_37 = rel_code_37 + right_part
                url1 = url + hgvs_38
                url2 = url + hgvs_37

                writer.writerow({'HGVSg': hgvs_38, 'HGVSg37': hgvs_37, 'url': url1,'url37': url2})

        return pd.read_csv(hgvs_file_name)

def check_chr_pattern(df):
    pattern = c.chr_hgvs_pattern

    for col in df.columns:
        current_col = df[col]

        count_matches = 0

        for i in range(len(df)):
            test_string = current_col[i]

            #print(test_string)

            if re.search(pattern, test_string):
                count_matches+=1

        if count_matches >= 0.8*len(df):
            chr_hgvs_col = col


            break

    try:
        df['HGVSg'] = df[chr_hgvs_col]
        hgvs_list = df['HGVSg']

        return hgvs_list

    except:
        return []

def check_hgvs_pattern(df):
    pattern = c.clean_pattern

    for col in df.columns:
        current_col = df[col]

        count_matches = 0

        for i in range(len(df)):
            test_string = current_col[i]
            print('test string: ', test_string)
            #print(test_string)

            if re.search(pattern, test_string):
                count_matches+=1
        if count_matches >= 0.8*len(df):
            hgvs_col = col
            print('clean_hgvs_col ', col )

            break

    try:
        df['HGVSg'] = df[hgvs_col]
        hgvs_list = df['HGVSg']

        return hgvs_list
    except:
        return []


def pipeline_vocab(hgvs_list):
    build_file = create_build_file(c.assembly_dir_path + 'GCF_000001405.26_GRCh38_assembly_report.txt')
    build_file2 = create_build_file(c.assembly_dir_path + 'GCF_000001405.13_GRCh37_assembly_report.txt')
    # TBA


if __name__ == '__main__':
    filename_vcf_gz_array = os.listdir(c.input_dir_path)

    for filename in filename_vcf_gz_array:
        out = pipeline(filename)
        if out == 'wrong':
            continue
