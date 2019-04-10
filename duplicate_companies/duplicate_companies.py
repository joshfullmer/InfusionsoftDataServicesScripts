import datetime
import sys

import jellyfish  # http://jellyfish.readthedocs.io/en/latest/comparison.html
import pandas as pd


def get_jw_similarity(string1, string2):
    """Returns the Jaro-Winkler distance for two strings
    The two strings are first stripped of common company suffixes
    https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance
    """
    string1 = strip_company(string1)
    string2 = strip_company(string2)
    return jellyfish.jaro_winkler(string1, string2)


def strip_company(string):
    """Gets rid of common company suffixes, and strips ending
    whitespace and commas"""
    string = string.replace('Inc.', '')
    string = string.replace('Inc', '')
    string = string.replace('inc', '')
    string = string.replace('LLC', '')
    string = string.replace('llc', '')
    string = string.replace('Ltd.', '')
    string = string.replace('Ltd', '')
    string = string.rstrip()
    string = string.rstrip(',')
    return string


start = datetime.datetime.now()
df = pd.read_csv('company_export.csv')
df = df.dropna()
rows_list = []
for index, row in df.iterrows():

    sys.stdout.write("\r{} rows completed.".format(index))
    sys.stdout.flush()

    # Get only the companies that have the same first 3 characters
    # This aids in cutting down the overall performance
    matches = df[df.Company.str.startswith(row.Company[0:3])].copy()

    # Remove the current row from the matches
    matches.drop(index, inplace=True)
    if not matches.empty:
        # Adds Jaro-Winkler distance as new column
        matches['Similarity'] = matches.apply(
            lambda x: get_jw_similarity(x.Company, row.Company), axis=1)

        for index2, row2 in matches.iterrows():
            # Threshold check for company name similarity
            if row2.Similarity >= 0.925:
                flip_dix = {'orig_id': row2.Id,
                            'dupe_id': row.Id,
                            'Name1': row2.Company,
                            'Name2': row.Company}
                # Checks if the mirror exists in the list of dicts
                if flip_dix not in rows_list:
                    dix = {'orig_id': row.Id,
                           'dupe_id': row2.Id,
                           'Name1': row.Company,
                           'Name2': row2.Company}
                    rows_list.append(dix)

output = pd.DataFrame(rows_list)
output.to_csv('duplicate_companies.csv', index=False)

print(datetime.datetime.now() - start)
