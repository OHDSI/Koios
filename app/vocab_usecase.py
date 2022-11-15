import psycopg2
import re
import pandas as pd
import app.constants as c
from app.vcf_extraction import pipeline_vocab


def run_vocab():
    conn = psycopg2.connect(database="postgres",
                            host="149.56.241.161",
                            user='pwd',
                            password='usr',
                            port="5555")

    cursor = conn.cursor()

    query = "SELECT * FROM dev_cgi.genomic_cgi_source gen"

    cursor.execute(query)
    records = cursor.fetchall()

    df = pd.DataFrame(records)

    pattern = c.clean_pattern

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