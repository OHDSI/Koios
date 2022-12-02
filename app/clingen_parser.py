import requests
import json
import urllib3
import csv
import time
import random
import pandas as pd
from app.constants import hgvsg_folder, temp_folder, hgvsg_folder_path, project_dir
from flask import session


def parse_clingen(hgvsg_df, current_filename, vcf_mode=False, mult_build_mode=False):
    hgvsg_df = hgvsg_df.reset_index()
    file_length = len(hgvsg_df['HGVSg'])

    http = urllib3.PoolManager()
    url = 'http://reg.test.genome.network/allele?hgvs='

    #parsed_file_name = hgvsg_folder_path + current_filename + '_clingen.csv'
    parsed_file_name = hgvsg_folder_path + 'outputClingen_' + session["RNDUSERSTR"] + '.csv'


    with open(parsed_file_name, 'w', encoding='utf-8') as csvfile:
        #fieldnames = ['HGVSg_vcf', 'link', 'communityStandardTitle', 'allele_class', 'type',
        #              'chromosome', 'allele_n', 'hgvs', 'hgvs_n', 'hgvs_referenceGenome',
        #              'hgvs_referenceSequence']

        if vcf_mode:
            fieldnames = ['filename', 'hgvsg', 'timestamp']
        else:
            fieldnames = ['source_concept_id', 'hgvsg', 'timestamp']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()

        print('\nStarting ClinGen parser... ')

        print('\nOpened file: ', current_filename, '\twith ', file_length, ' hgvs')

        ii = 1

        for i, seq in enumerate(hgvsg_df['HGVSg']):

            if mult_build_mode:

                try:
                    seq2 = hgvsg_df['HGVSg37'][i]
                    url_2 = hgvsg_df['url37'][i]
                    mode_37_38 = True
                except:
                    mode_37_38 = False



                # convert symbol > to special code %3E
            url_1 = url + requests.utils.quote(seq)

            print('#', ii, 'hgvs_name: ', seq, ': ', url_1)
            ii += 1
            res = http.request('GET', url_1)
            data = json.loads(res.data)

            if mult_build_mode:
                if mode_37_38:
                    res37 = http.request('GET', url_2)
                    data37 = json.loads(res37.data)

                    try:
                        communityStandardTitle = data.get('communityStandardTitle')
                    except:
                        pass
                    try:
                        communityStandardTitle37 = data37.get('communityStandardTitle')
                    except:
                        pass

                    try:
                        if len(communityStandardTitle) > 0:
                            data = data
                            seq = seq
                    except:
                        pass
                    try:
                        if len(communityStandardTitle37) > 0:
                            data = data37
                            seq = seq2
                    except:
                        pass

                    try:
                        if len(communityStandardTitle37) > 0 and len(communityStandardTitle) > 0:
                            continue
                    except:
                        pass

            try:
                communityStandardTitle = data.get('communityStandardTitle')
                if communityStandardTitle != None:
                    communityStandardTitle = communityStandardTitle[0]
                if vcf_mode:
                    writer.writerow({'filename': current_filename, 'hgvsg': seq, 'timestamp': time.ctime()})
                else:
                    writer.writerow({'source_concept_id': current_filename, 'hgvsg': seq, 'timestamp': time.ctime()})



                t = data.get('type')

                if t == 'nucleotide':

                    genomicAlleles = data.get('genomicAlleles')
                    if genomicAlleles != None:
                        num_alleles = len(genomicAlleles)

                        # PART1: Genomic Alleles
                        for iter in range(num_alleles):
                            allele_class = 'genomicAlleles'
                            allele_n = iter

                            gen = genomicAlleles[iter]

                            chromosome = gen.get('chromosome')

                            hgvs_referenceGenome = gen.get('referenceGenome')
                            hgvs_referenceSequence = gen.get('referenceSequence')

                            # print('chromosome: ', chromosome)

                            hgvs_all = gen.get('hgvs')

                            if hgvs_all != None:
                                len_hgvs = len(hgvs_all)
                                for i in range(len_hgvs):
                                    hgvs_n = i
                                    hgvs = hgvs_all[i]
                                    # print('hgvs #', hgvs_n, ' : ', hgvs)
                                    '''
                                    writer.writerow({'HGVSg_vcf': seq, 'link': url_1,
                                                     'communityStandardTitle': communityStandardTitle,
                                                     'allele_class': allele_class, 'type': t, 'chromosome': chromosome,
                                                     'allele_n': allele_n, 'hgvs': hgvs, 'hgvs_n': hgvs_n,
                                                     'hgvs_referenceGenome': hgvs_referenceGenome,
                                                     'hgvs_referenceSequence': hgvs_referenceSequence})
                                    '''
                                    if vcf_mode:
                                        writer.writerow({'filename': current_filename, 'hgvsg': hgvs,
                                                         'timestamp': time.ctime()})

                                    else:
                                        writer.writerow({'source_concept_id': current_filename, 'hgvsg': hgvs, 'timestamp': time.ctime()})
                                    # print('hhh: ', hgvs, 'n: ', hgvs_n)
                            else:
                                hgvs_n = 1
                                hgvs = hgvs_all
                                '''
                                writer.writerow(
                                    {'HGVSg_vcf': seq, 'link': url_1, 'communityStandardTitle': communityStandardTitle,
                                     'allele_class': allele_class, 'type': t, 'chromosome': chromosome,
                                     'allele_n': allele_n, 'hgvs': hgvs, 'hgvs_n': hgvs_n,
                                     'hgvs_referenceGenome': hgvs_referenceGenome,
                                     'hgvs_referenceSequence': hgvs_referenceSequence})
                                '''

            except:
                print('error: ', seq)
                #writer.writerow({'HGVSc_vsf': seq, 'link': url_1,
                #                 'communityStandardTitle': communityStandardTitle, 'type': 'error'})
                pass


    return pd.read_csv(parsed_file_name)