def predictor(args):
    import yaml
    import pandas as pd
    import pkg_resources
    import pyranges as pr
    from tqdm import tqdm
    import subprocess
    import gzip
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn import metrics
    from sklearn.metrics import roc_auc_score

    if args.verbose:
        print("postprocessing de novo variants from ", args.slivar)

    df = pd.read_csv(args.slivar, sep='\t')
    df = df[~df['chr:pos:ref:alt'].str.contains('*', regex=False)]
    # if not args.X:
    df = df[df['#mode'].str.startswith('d')]
    # else:
    #     df = df[df['#mode'].str.startswith('x')]
    df[['chr', 'position', 'ref', 'alt']] = df['chr:pos:ref:alt'].str.split(':', expand=True)
    df['allele_balance'] = df['allele_balance(sample,dad,mom)'].str.split(',').str[0].astype(float)
    df['depth'] = df['depths(sample,dad,mom)'].str.split(',').str[0].astype(float)
    def variant_len(variant):
        v = variant.split(':')
        return( abs( len(v[2]) - len(v[3]) ) )
    df['variant_size'] = df['chr:pos:ref:alt'].apply(variant_len)

    df_tmp = df[['sample_id', 'chr:pos:ref:alt']].groupby(['sample_id']).count().reset_index()
    df_tmp.columns = ['sample_id', 'count']
    Q1 = df_tmp['count'].quantile(0.25)
    Q3 = df_tmp['count'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df_tmp[ (df_tmp['count'] < (Q1 - 1.5*IQR)) | (df_tmp['count'] > (Q3 + 1.5*IQR)) ]['sample_id']
    if args.verbose:
        print(f"{len(outliers)} outliers in number of DNM are detected using the IQR method before prediction.")
    df['outlier_dnm'] = df['sample_id'].apply(lambda x: True if x in list(outliers) else False)

    # def isPAR(row):
    #     if args.ref == 'GRCh37' or args.ref == 'hg19':
    #         PAR1_start = 60001
    #         PAR1_end = 2699520
    #         PAR2_start = 154931044
    #         PAR2_end = 155260560
    #     elif args.ref == 'GRCh38' or args.ref == 'hg38':
    #         PAR1_start = 10001
    #         PAR1_end = 2781479
    #         PAR2_start = 155701383
    #         PAR2_end = 156030895
    #     else:
    #         return False
    #     pos = int(row['position'])
    #     if pos>PAR1_start and pos<PAR1_end:
    #         return True
    #     if pos>PAR2_start and pos<PAR2_end:
    #         return True
    #     return False
    # if args.X:
    #     df['isPAR'] = df.apply(isPAR, axis=1)

    df_learn = pd.read_csv(pkg_resources.resource_filename('ghfc_utils', f'resources/model.{args.model}.tsv.gz'), sep='\t')

    X_train, X_test, y_train, y_test = train_test_split( np.array(df_learn[['allele_balance', 'depth', 'variant_size']]), np.array(df_learn['validated']), test_size=0.25, random_state=0)
    if args.verbose:
        print('train', X_train.shape, y_train.shape)
        print('test', X_test.shape, y_test.shape)
    X = np.array(df[['allele_balance', 'depth', 'variant_size']])
    clf = RandomForestClassifier(max_depth=3, random_state=0)
    clf = clf.fit(X_train, y_train)
    if args.verbose:
        print("score", clf.score(X_test, y_test))
    scores = clf.predict_proba(X_test)[:,1:].flatten()
    fpr, tpr, thresholds = metrics.roc_curve(y_test, scores, pos_label=True)
    df_roc_tmp = pd.DataFrame([fpr, tpr, thresholds]).T
    df_roc_tmp.columns = ['fpr', 'tpr', 'thresholds']
    auc = "{:.3f}".format(roc_auc_score(y_test, scores))
    df_roc_tmp['type'] = "RF - All - "+auc
    scores = clf.predict_proba(X)[:,1:].flatten()
    df['prediction_dnm'] = scores
    def get_threshold_fpr(fpr):
        return float(df_roc_tmp.iloc[ (df_roc_tmp['fpr']-fpr).abs().argsort()[:1],2].iloc[0])
    df[f'isDNM_fpr{args.fpr}'] = df['prediction_dnm'].apply(lambda x: True if x>get_threshold_fpr(args.fpr) else False)
    if args.verbose:
        print(f'Applying a cutoff for an FPR of {args.fpr} (cutoff is prediction>{get_threshold_fpr(args.fpr)})')
    df_valid = df[df[f'isDNM_fpr{args.fpr}']]

    df_tmp = df_valid[['sample_id', 'chr:pos:ref:alt']].groupby(['sample_id']).count().reset_index()
    df_tmp.columns = ['sample_id', 'count']
    Q1 = df_tmp['count'].quantile(0.25)
    Q3 = df_tmp['count'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df_tmp[ (df_tmp['count'] < (Q1 - 1.5*IQR)) | (df_tmp['count'] > (Q3 + 1.5*IQR)) ]['sample_id']
    if args.verbose:
        print(len(outliers), "outliers in number of DNM are detected using the IQR method after the postprocessing.")
    df['outlier_dnm'] = df['sample_id'].apply(lambda x: True if x in list(outliers) else False)
    if args.verbose and (len(outliers)>0):
        print('list of outliers:',';'.join(outliers))
    df.drop(['chr', 'position', 'ref', 'alt', 'variant_size', 'allele_balance', 'depth'], axis=1, inplace=True)
    df.to_csv(args.output, sep='\t', index=False)

def main(args=None):
    import argparse
    parser = argparse.ArgumentParser(description='A tool to predict the veracity of de novo variants in a slivar.')
    parser.add_argument('slivar', help='slivar file to reannotate')
    parser.add_argument('output', help='annotated slivar file')
    parser.add_argument('--fpr', dest='fpr', default=0.05, help='false positive rate cutoff for prediction (default 0.05)', type=float)
    parser.add_argument('-m', '--model', dest='model', default='WGS', help='model to use for the machine learning (default WGS)', type=str)
    # parser.add_argument('-r', '--ref', dest='ref', default="GRCh37", help='reference genome shortname (default GRCh37)')
    parser.add_argument('-v', '--verbose', dest='verbose', help='activate verbose mode', default=False, action='store_true')
    predictor(parser.parse_args(args))

if __name__ == '__main__':
    main()