from models import *  # COLOCAR O PONTO DE VOLTA (.MODELS)
import json
import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Process some files with different tools.')

    subparsers = parser.add_subparsers(dest='tool', required=True, help='')

    # sdf
    parser_sdf = subparsers.add_parser('sdf', help='Process SDF files.')

    parser_sdf.add_argument('-i', '--input_file', type=str, required=True, help='Pharmit analysis SDF file')
    parser_sdf.add_argument('-db', '--database', type=str, required=True, help='Name of the database used in the search')
    parser_sdf.add_argument('-n', '--batch', type=int, default=299, help='Number of molecules in each file')
    parser_sdf.add_argument('-af', '--minimizedAffinity', type=float, help='Filter by pharmit score')

    # score
    parser_score = subparsers.add_parser('score', help='Tool that creates an admet analysis spreadsheet, listing the best molecule options by score.')

    parser_score.add_argument('-i', '--input_file', type=str, required=True, help='Admet analysis of admetlab 3.0')
    parser_score.add_argument('-t', '--best_hits', type=int, default=None, help='Number of molecules to be selected as the best from the analysis of the admetlab3.0 spreadsheet')
    parser_score.add_argument('-s', '--sdf', type=str, required=True, help='Pharmit analysis SDF file')
    parser_score.add_argument('-w', '--weights',
                    type=str,
                    help='Json file that changes the weights assigned in the analysis of the admetlab 3.0 spreadsheet')

    args = parser.parse_args()

    if args.tool == 'sdf':
        process_sdf(args.input_file, args.database, args.batch, args.minimizedAffinity)

    elif args.tool == 'score':
        process_score(args.input_file, args.best_hits, args.sdf, args.weights)

def process_sdf(input_file, database, batch, affinity):

    sdf_instance = Sdf()

    sdf_instance.process_sdf(input_file, database, batch, affinity)

def process_score(input_file, best_hits, sdf, weights):

    
    if weights is not None:
        with open(weights, "r", encoding="utf-8") as f:
            weights = json.loads(f.read())
    
    extract_instance = Extract()
    analysis_instance = AdmetSpreadsheet()
    spreadsheet_instance = Spreadsheet()

    df = extract_instance.extract(input_file, sdf)
    df = analysis_instance.process_data(df, weights)

    df = spreadsheet_instance.spreadsheet_output(df)

    if best_hits is not None:
        tops_csv_path = os.path.join('score', f'scoreadmet_{best_hits}_tops.csv')
        top_df = df.head(best_hits)
        top_df.to_csv(tops_csv_path, index=False)

if __name__ == '__main__':
    main()


