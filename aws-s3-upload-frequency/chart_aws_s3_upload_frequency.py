"""
The script solves problem of dumping last updated timestamp for objects uploads under particular S3 path.

Approach:
    * Use boto3 list-objects API to pull info for all the files under S3 path ( can take long time )
    * Dump the extracted data to JSON file in the local folder

Parameters:
    --s3-url s3://<bucket>/s3/path/
        S3 path to process the files under ( recursively )
    --output-label <customer-name>
        Used to generate output file
        <customer-name>-list-objects-out.json
"""
import json
import boto3
import argparse
import pandas as pd
from tqdm import tqdm
import plotly.offline as py
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from datetime import date, datetime, timezone, timedelta

class CONFIG:
    class ARGS:
        s3url = None
        label = None 
        cutoff_days = 30 

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
    args = parser.parse_args()
    CONFIG.ARGS.s3url = args.s3_url
    CONFIG.ARGS.label  = args.output_label


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
    
    out_file_name = f'{CONFIG.ARGS.label}-list-objects-out.json'
    print(f'Saving S3 stats to file ')
    with open(out_file_name, 'w') as out_file:
        json.dump(s3_scan_output, fp=out_file, default=json_serialize)


if __name__ == '__main__':
    parse_args()
    s3_stats = scan_s3_path(from_s3_url=CONFIG.ARGS.s3url)
    save_stats_to_file(s3_stats)
    df2 = pd.DataFrame.from_dict(
        data = s3_stats,
        orient='index', 
        columns=['last_updated']
    )
    filtered_df = df2[ df2['last_updated'] > datetime.now(tz=timezone.utc) - timedelta(days=CONFIG.ARGS.cutoff_days) ]
    stats_df = filtered_df.resample('5min', on='last_updated').count()
    chart = {
        'x' : stats_df.index,
        'y' : stats_df['last_updated'],
        'type': 'bar'
    }
    py.plot({'data': [chart]}, filename=f'{CONFIG.ARGS.label}-frequency-upload-chart.html')
    
