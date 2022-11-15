import pandas as pd
from csv import writer
import app.constants as c
import os


def map_to_omop(parsed_df,current_filename, vcf_mode = False):
    print(c.split_line_thin)
    print('\nMapping ClinGen output to OMOP Genomic vocabulary')
    vocabulary_omop = pd.read_csv(c.vocab_path + 'CONCEPT_SYNONYM.csv', delimiter='\t')

    matched_to_synonyms = parsed_df.merge(vocabulary_omop, left_on = 'hgvsg',
                                          right_on = 'concept_synonym_name', how='left')
    matched_to_synonyms_inner = parsed_df.merge(vocabulary_omop, left_on='hgvsg',
                                          right_on='concept_synonym_name')
    #matched_to_synonyms.to_csv(c.output_dir_path + current_filename + '_OMOP' + '.csv', index=False)
    matched_to_synonyms['target_concept_id'] = matched_to_synonyms['concept_id']
    matched_to_synonyms_inner['target_concept_id'] = matched_to_synonyms_inner['concept_id']
    matched_to_synonyms = matched_to_synonyms.astype({"target_concept_id": int}, errors='ignore')

    if vcf_mode:
        matched_to_synonyms = matched_to_synonyms[['filename','hgvsg', 'target_concept_id', 'timestamp']]
    else:
        matched_to_synonyms = matched_to_synonyms[['source_concept_id', 'hgvsg', 'target_concept_id', 'timestamp']]

    filename = c.output_dir_path + 'outputOMOP_' + c.random_user_substring + '.csv'
    matched_to_synonyms.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False, float_format='%.0f')

    print(c.split_line_thin)
    num_matches = len(matched_to_synonyms_inner)
    print('The # of matches found: ', num_matches)

    if num_matches != 0:
        print(matched_to_synonyms_inner[['hgvsg', 'target_concept_id']])

    return matched_to_synonyms