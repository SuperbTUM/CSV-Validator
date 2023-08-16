import numpy as np
import pandas as pd
import argparse
import math


def compare(source_file: str,
            target_file: str,
            major_key: str,
            ignored_key: str):

    source = pd.read_csv(source_file)
    target = pd.read_csv(target_file)
    if not major_key:
        major_key = source.columns[0]

    source_cols = source.columns
    target_cols = target.columns
    _, source_indices, _ = np.intersect1d(source_cols, target_cols, return_indices=True)
    intersect = source_cols[sorted(source_indices)]

    source = source.loc[:, intersect]
    target = target.loc[:, intersect]

    joined = pd.merge(source, target, how='inner', on=[major_key])

    left, right = joined.iloc[:, :len(intersect)], pd.concat([joined.iloc[:, 0], joined.iloc[:, len(intersect):]], axis=1)
    left = left.rename(columns={left.columns[i]: intersect[i] for i in range(len(left.columns))})
    right = right.rename(columns={right.columns[i]: intersect[i] for i in range(len(right.columns))})
    left = left.sort_values(major_key, ignore_index=True)
    right = right.sort_values(major_key, ignore_index=True)

    for i, (source_row, target_row) in enumerate(zip(left.itertuples(index=True, name='Pandas'), right.itertuples(index=True, name='Pandas'))):
        for ii, attr_name in enumerate(intersect):
            if attr_name in ignored_key.split(','):
                continue
            val1 = getattr(source_row, attr_name)
            val2 = getattr(target_row, attr_name)
            if type(val1) in (float, int) and type(val2) in (float, int):
                if math.isnan(val1) or math.isnan(val2):
                    continue
                if not np.isclose(val1, val2, rtol=0.01, atol=0.5):
                    print("Warning! {} on row {} is not a good match, source {} target {}!".format(attr_name, i, val1, val2))
            else:
                if val1 in ('', 'nan', None) or val2 in ('', 'nan', None):
                    continue
                if val1 != val2:
                    print("Warning! {} on row {} is not a good match,  source {} target {}!".format(attr_name, i, val1, val2))


def parse():
    args = argparse.ArgumentParser()
    args.add_argument('--source', '-s', type=str, required=True)
    args.add_argument('--target', '-t', type=str, required=True)
    args.add_argument('--major_key', '-key', type=str, default='')
    args.add_argument('--ignored_key', '-ignore', type=str, default='')
    return args.parse_args()


if __name__ == "__main__":
    params = parse()
    compare(params.source, params.target, params.major_key, params.ignored_key)

