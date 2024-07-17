def reannotate(args):
    import yaml
    import pandas as pd
    import pkg_resources
    import pyranges as pr
    from tqdm import tqdm
    import subprocess
    import gzip

    # reading the configuraiton yaml file
    config = yaml.safe_load(open(args.configuration))
    chunk_nb=0
    output_created = False

    nb_chunks = float('inf')
    if args.progress:
        if args.slivar.endswith('.gz'):
            with gzip.open(args.slivar, 'rb') as f:
                for i, l in enumerate(f):
                    pass
            nb_chunks = i//args.chunksize
        else:
            len_input = subprocess.run(['wc','-l',args.slivar], stdout=subprocess.PIPE, text=True)
            nb_chunks = int(len_input.stdout.strip().split(' ')[0])//args.chunksize


    with pd.read_csv(args.slivar, sep='\t', dtype="string", chunksize=args.chunksize) as reader:
        for df in tqdm(reader, desc='chunks analyzed', unit='chunk', total=nb_chunks+1, disable=(not args.progress)):
            if args.verbose:
                print('chunk number:', chunk_nb)
            chunk_nb+=1

            # filtering on samples
            if 'sample-file' in config:
                samples = list(pd.read_csv(config['sample-file'], sep='\t', names=['barcode'])['barcode'])
                df = df[df['sample_id'].isin(samples)].copy()

            # separating transcript for each variants
            df[config['slivar-field-name']] = df[config['slivar-field-name']].str.split(';')
            df = df.explode(config['slivar-field-name'])
            if args.verbose:
                print('making a total of', len(df), 'transcripts impacted')

            if len(df)<=0:
                continue

            # splitting the slivar transcript line, be careful, changing depending on slivar options, parameters in the config file are important
            df[config['slivar-field-decomposed']] = df[config['slivar-field-name']].str.split('/', expand=True)
            # TEMP drop config['slivar-field-name']
            df.drop(['gene', 'highest_impact', config['slivar-field-name']], axis=1, inplace=True)

            # filtering based on ENSG
            if 'geneset-file' in config:
                geneset = list(pd.read_csv(config['geneset-file'], sep='\t', names=['name'])['name'])
                df = df[df['ENSG'].isin(geneset)]
                if args.verbose:
                    print('after geneset filtering:', len(df), 'transcripts impacted')

            # importing impacts configuration
            yaml_impacts = yaml.safe_load(open(pkg_resources.resource_filename('ghfc_utils', 'resources/impacts.yaml')))
            impact_categories = list(yaml_impacts.keys())
            dict_rev_impacts = {}
            for k,v in yaml_impacts.items():
                for x in v:
                    dict_rev_impacts[x] = str(k)
                    dict_rev_impacts[x+"_variant"] = str(k)

            # filtering based on impacts
            list_impacts = []
            if 'impact-filter' in config:
                list_impacts = config['impact-filter'] + [i+"_variant" for i in config['impact-filter']]
            if 'impact-categories-filter' in config:
                for c in config['impact-categories-filter']:
                    list_impacts = list_impacts + [i for i in yaml_impacts[c]] + [i+"_variant" for i in yaml_impacts[c]]
            list_impacts = list(set(list_impacts))
            if ('impact-filter' in config) or ('impact-categories-filter' in config):
                df = df[df['impact'].isin(list_impacts)]
                if args.verbose:
                    print('after impact filtering:', len(df), 'transcripts impacted')

            # filters specific to missenses
            if 'missense-filter' in config:
                df[config['missense-filter']['mpc']['field']] = pd.to_numeric(df[config['missense-filter']['mpc']['field']], errors='coerce')
                df[config['missense-filter']['cadd']['field']] = pd.to_numeric(df[config['missense-filter']['cadd']['field']], errors='coerce')
                df[config['missense-filter']['alphamissense']['field']] = pd.to_numeric(df[config['missense-filter']['alphamissense']['field']], errors='coerce')
                if config['missense-filter']['condition'] == 'cadd_if_no_mpc':
                    if args.verbose:
                        print('must pass the MPC filter, if the MPC is unavailable, must pass the CADD.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] >= config['missense-filter']['mpc']['min']) & 
                            (df[config['missense-filter']['mpc']['field']] < config['missense-filter']['mpc']['max'])
                        ) |
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] == -1) & 
                            (df[config['missense-filter']['cadd']['field']] >= config['missense-filter']['cadd']['min']) &
                            (df[config['missense-filter']['cadd']['field']] < config['missense-filter']['cadd']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'cadd_and_mpc':
                    if args.verbose:
                        print('must pass both the MPC and the CADD filters.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] >= config['missense-filter']['mpc']['min']) & 
                            (df[config['missense-filter']['mpc']['field']] < config['missense-filter']['mpc']['max']) & 
                            (df[config['missense-filter']['cadd']['field']] >= config['missense-filter']['cadd']['min']) &
                            (df[config['missense-filter']['cadd']['field']] < config['missense-filter']['cadd']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'cadd_or_mpc':
                    if args.verbose:
                        print('must pass the MPC filter OR the CADD filter.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] >= config['missense-filter']['mpc']['min']) & 
                            (df[config['missense-filter']['mpc']['field']] < config['missense-filter']['mpc']['max'])
                        ) |
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['cadd']['field']] >= config['missense-filter']['cadd']['min']) &
                            (df[config['missense-filter']['cadd']['field']] < config['missense-filter']['cadd']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'mpc_only':
                    if args.verbose:
                        print('must pass the MPC filter.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] >= config['missense-filter']['mpc']['min']) & 
                            (df[config['missense-filter']['mpc']['field']] < config['missense-filter']['mpc']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'cadd_only':
                    if args.verbose:
                        print('must pass the CADD filter.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['cadd']['field']] >= config['missense-filter']['cadd']['min']) &
                            (df[config['missense-filter']['cadd']['field']] < config['missense-filter']['cadd']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'cadd_if_no_mpc_or_am':
                    if args.verbose:
                        print('must pass the MPC filter or the AlphaMissense, if unavailable, must pass the CADD.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] >= config['missense-filter']['mpc']['min']) & 
                            (df[config['missense-filter']['mpc']['field']] < config['missense-filter']['mpc']['max'])
                        ) |
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['alphamissense']['field']] >= config['missense-filter']['alphamissense']['min']) & 
                            (df[config['missense-filter']['alphamissense']['field']] <= config['missense-filter']['alphamissense']['max'])
                        ) |
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] == -1) & 
                            (df[config['missense-filter']['alphamissense']['field']] == -1) & 
                            (df[config['missense-filter']['cadd']['field']] >= config['missense-filter']['cadd']['min']) &
                            (df[config['missense-filter']['cadd']['field']] < config['missense-filter']['cadd']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'mpc_and_am':
                    if args.verbose:
                        print('must pass both the MPC and the AlphaMissense filters.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] >= config['missense-filter']['mpc']['min']) & 
                            (df[config['missense-filter']['mpc']['field']] < config['missense-filter']['mpc']['max']) & 
                            (df[config['missense-filter']['alphamissense']['field']] >= config['missense-filter']['alphamissense']['min']) &
                            (df[config['missense-filter']['alphamissense']['field']] <= config['missense-filter']['alphamissense']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'mpc_or_am':
                    if args.verbose:
                        print('must pass the MPC filter OR the AlphaMissense filter.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['mpc']['field']] >= config['missense-filter']['mpc']['min']) & 
                            (df[config['missense-filter']['mpc']['field']] < config['missense-filter']['mpc']['max'])
                        ) |
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['alphamissense']['field']] >= config['missense-filter']['alphamissense']['min']) &
                            (df[config['missense-filter']['alphamissense']['field']] <= config['missense-filter']['alphamissense']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                elif config['missense-filter']['condition'] == 'am_only':
                    if args.verbose:
                        print('must pass the AlphaMissense filter.')
                    df = df[ 
                        (
                            df['impact'].isin(['missense', 'missense_variant']) & 
                            (df[config['missense-filter']['alphamissense']['field']] >= config['missense-filter']['alphamissense']['min']) &
                            (df[config['missense-filter']['alphamissense']['field']] <= config['missense-filter']['alphamissense']['max'])
                        ) |
                        ( ~df['impact'].isin(['missense', 'missense_variant']) )
                    ]
                else:
                    if args.verbose:
                        print('no specific filters applied to missenses.')
            if args.verbose:
                print('after missense filtering:', len(df), 'transcripts impacted')

            # filters specific to inframe variants
            # TODO

            # filtering on frequency
            if 'gnomad-filter' in config:
                df[config['gnomad-filter']['field']] = pd.to_numeric(df[config['gnomad-filter']['field']], errors='coerce')
                df = df[
                    (df[config['gnomad-filter']['field']] >= config['gnomad-filter']['min']) &
                    (df[config['gnomad-filter']['field']] <= config['gnomad-filter']['max'])
                    ]
                if args.verbose:
                    print('after gnomad filtering:', len(df), 'transcripts impacted')

            # sort by transcript "importance" depending on config file priority
            # make categorical for sort to work on the following categories: impact, LoF, canonical...
            df['impact-category'] = df['impact'].map(dict_rev_impacts, na_action='ignore')
            df['impact-category'] = pd.Categorical(df['impact-category'], categories = ['lof_high','lof_med', 'genic_high', 'genic_med', 'genic_low', 'other_high', 'other_low'], ordered = True)
            df['canonical'] = pd.Categorical(df['canonical'], categories = ['YES', ''], ordered = True)
            df['loftee'] = pd.Categorical(df['loftee'], categories = ['HC', 'OS', '', 'LC'], ordered = True)
            df.sort_values(['sample_id', 'chr:pos:ref:alt', 'ENSG']+config['ordering-priority'], inplace=True)

            # aggregating transcripts is done by droping duplicates and keeping only the first (as we sorted using our preferences)
            if not args.keep_all:
                df.drop_duplicates(subset = ['sample_id', 'chr:pos:ref:alt', 'ENSG'], keep = 'first', inplace=True)
            if args.verbose:
                print('after remerging transcripts:', len(df), 'variant/gene/sample')

            # filtering on pext
            if 'pext-filter' in config and (len(df)>0):
                df[['chr', 'position', 'ref', 'alt']] = df['chr:pos:ref:alt'].str.split(':', expand=True)
                def variant_len(variant):
                        v = variant.split(':')
                        return( abs( len(v[2]) - len(v[3]) ) )
                df['variant_size'] = df['chr:pos:ref:alt'].apply(variant_len)

                df_pext = pd.read_csv(config['pext-filter']['file'], sep='\t')
                df_pext.columns = ['Chromosome', 'Start', 'End', 'mean_brain', 'ensg', 'symbol']
                gr_pext = pr.PyRanges(df_pext)

                def get_pext2(gr_pext, ensg, symbol, chrom, position, impact, variant_size):
                    shift = 0
                    if impact in ['splice_donor', 'splice_acceptor']:
                        shift = 3

                    end = int(position)+shift+variant_size+1
                    start = int(position)-shift-variant_size

                    df_temp = gr_pext[chrom, start:end].as_df()
                    if df_temp.empty :
                        return -1
                    df_temp = df_temp[(df_temp['ensg']==ensg) | (df_temp['symbol']==symbol)]

                    if len(df_temp)>1:
                        return df_temp['mean_brain'].max()
                    if len(df_temp)==1:
                        return df_temp['mean_brain'].item()
                    return -1

                df[config['pext-filter']['field']] = df.apply(lambda x: get_pext2(gr_pext, x['ENSG'], x['symbol'], x['chr'], x['position'], x['impact'], x['variant_size']), axis=1)
                df = df[df[config['pext-filter']['field']]>=config['pext-filter']['min']]
                df.drop(['chr', 'position', 'ref', 'alt', 'variant_size'], axis=1, inplace=True)
                if args.verbose:
                    print('after pext filtering:', len(df), 'transcripts impacted')

            if 'lcr-filter' in config and (len(df)>0):
                df[['chr', 'position', 'ref', 'alt']] = df['chr:pos:ref:alt'].str.split(':', expand=True)
                def variant_len(variant):
                        v = variant.split(':')
                        return( abs( len(v[2]) - len(v[3]) ) )
                df['variant_size'] = df['chr:pos:ref:alt'].apply(variant_len)

                df_LCR = pd.read_csv(config['lcr-filter']['file'], sep='\t', dtype={'Chromosome':'str'}, names=['Chromosome', 'Start', 'End'])
                df_LCR = df_LCR[
                            ~df_LCR['Chromosome'].str.startswith('GL')
                            & ~df_LCR['Chromosome'].str.startswith('NC')
                            & ~df_LCR['Chromosome'].str.startswith('hs')
                            ]
                gr_LCR = pr.PyRanges(df_LCR)
                def isLCR(row):
                    start = int(row['position'])
                    end = start+1+int(row['variant_size'])
                    if len( gr_LCR[row['chr'], start:end] ) > 0:
                        return True
                    return False
                df['isLCR'] = df.apply(isLCR, axis=1)
                df.drop(['chr', 'position', 'ref', 'alt', 'variant_size'], axis=1, inplace=True)
                if config['lcr-filter']['filter']:
                    df = df[~df['isLCR']]
                    if args.verbose:
                        print('after lcr filtering:', len(df), 'transcripts impacted')

            # outputing processed file
            if len(df)>0 :
                if not output_created:
                    df.to_csv(args.output, sep='\t', index=False)
                    output_created = True
                else:
                    df.to_csv(args.output, sep='\t', index=False, mode='a', header=None)

def main(args=None):
    import argparse

    parser = argparse.ArgumentParser(description='A tool to filter and reannotate slivar files according to various parameters and genesets.')
    parser.add_argument('configuration', help='config file')
    parser.add_argument('slivar', help='slivar file to reannotate')
    parser.add_argument('output', help='annotated slivar file')
    parser.add_argument('-c', '--chunksize', dest='chunksize', default=100000, help='size of the chunks read from the input (default 100000)', type=int)
    parser.add_argument('-k', '--keep-all-transcripts', dest='keep_all', help='to keep all impacted transcript instead of the first', default=False, action='store_true')
    parser.add_argument('-p', '--progress', dest='progress', help='display a progress bar', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', dest='verbose', help='activate verbose mode', default=False, action='store_true')

    reannotate(parser.parse_args(args))

if __name__ == '__main__':
    main()