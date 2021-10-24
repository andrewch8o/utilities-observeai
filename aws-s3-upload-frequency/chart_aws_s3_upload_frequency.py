"""
The script solves problem of dumping last updated timestamp for objects uploads under particular S3 path.

Approach:
    * Use boto3 list-objects API to pull info for all the files under S3 path ( can take long time )
    * Dump the extracted data to JSON file in the local folder
    * Generage interactive chart exported as HTML file

Parameters:
    --s3-url s3://<bucket>/s3/path/
        S3 path to process the files under ( recursively )
    --output-label <customer-name>
        Used to generate output file
        <customer-name>-list-objects-out.json
        <customer-name>-upload-frequency-chart.html
"""
import os
import json
import boto3
import argparse
import pandas as pd
from tqdm import tqdm
import plotly.offline as py
from urllib.parse import urlparse
from datetime import date, datetime, timezone, timedelta

class CONFIG:
    class ARGS:
        s3url   = None
        label   = None 
        nocache = False
        cutoff_days = 30
        @classmethod
        def get_data_dump_filename(cls):
            return f's3-scan-dump-{cls.label}.json'
        @classmethod
        def get_visualization_filename(cls):
            return f's3-up-vis-{cls.label}.html'

def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, 
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--s3-url',
        required=True,
        help='S3 path to scan recursively')
    parser.add_argument(
        '--output-label', 
        required=True, 
        help='Label to use for output files (dashboard name, for example)')
    parser.add_argument(
        '--nocache',
        required=False,
        action='store_true', 
        help='Instructs the script to ignore previously fetched JSON file and re-scan S3')
    args = parser.parse_args()
    CONFIG.ARGS.s3url = args.s3_url
    CONFIG.ARGS.label  = args.output_label
    CONFIG.ARGS.nocache = args.nocache


def scan_and_dump_s3_loc():
    '''Checks cache conditions. Skips S3 scan if cache file exists and nocase is not used'''
    dump_file_name = CONFIG.ARGS.get_data_dump_filename()
    if os.path.isfile(dump_file_name) and not CONFIG.ARGS.nocache:
        print(f'Skipping S3 scan. Using cached version of S3 dump:{dump_file_name}')
        return
    print(f'Commencing page-by-page S3 API scan [may take long time on large volumes]')
    s3_stats = scan_s3_path(from_s3_url=CONFIG.ARGS.s3url) 
    save_stats_to_file(s3_stats)


def scan_s3_path(from_s3_url):
    client = boto3.client('s3')
    print(f'Scanning {from_s3_url}')
    s3_url = urlparse(from_s3_url)
    s3_bucket = s3_url.netloc
    s3_prefix = s3_url.path[1:]
    paginator = client.get_paginator('list_objects_v2')
    listing = {}
    pbar_iterator = tqdm(paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix))
    pbar_iterator.set_description_str('Iterating over S3 API response pages')
    for page in pbar_iterator:
        try:
            page_contents = page['Contents']
            listing.update( { rec['Key'] : rec['LastModified'] for rec in page_contents } )
        except KeyError:
            # Ignoring KeyError that may occur on "folders" (empty objects)
            pass
    return listing


def save_stats_to_file(s3_scan_output: dict):
    '''Saves data obtained from S3 listing to file'''
    def json_serialize(obj):
        '''Handles serialization of datetime objects'''
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f'Type {type(obj)} serialization not implemented')
    
    out_file_name = CONFIG.ARGS.get_data_dump_filename()
    print(f'Saving S3 stats to file ')
    with open(out_file_name, 'w') as out_file:
        json.dump(s3_scan_output, fp=out_file, default=json_serialize)


def visualize_data_dump():
    '''Load JSON object from the previously generated dump file
        and generates visualization'''
    dump_file_name = CONFIG.ARGS.get_data_dump_filename()
    
    def parse_values_as_isodatetime(dict):
        '''Parses dictionary values as iso datetime values'''
        return { k:datetime.fromisoformat(dict[k]) for k in dict.keys() }

    with open(dump_file_name) as in_file:
        s3_stats = json.load(
            fp=in_file,
            object_hook=parse_values_as_isodatetime)
    df2 = pd.DataFrame.from_dict(
        data = s3_stats,
        orient='index', 
        columns=['last_updated']
    )
    filtered_df = df2[ df2['last_updated'] > datetime.now(tz=timezone.utc) - timedelta(days=CONFIG.ARGS.cutoff_days) ]
    stats_df = filtered_df.resample('15min', on='last_updated').count()
    chart = {
        'x' : stats_df.index,
        'y' : stats_df['last_updated'],
        'type': 'bar'
    }
    py.plot({'data': [chart]}, filename=CONFIG.ARGS.get_visualization_filename())

if __name__ == '__main__':
    parse_args()
    scan_and_dump_s3_loc()
    visualize_data_dump()
    

