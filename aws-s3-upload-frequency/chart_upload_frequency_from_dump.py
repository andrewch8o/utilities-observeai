"""
The script solves problem of visualizing the data from S3 dump obtained via accompanying
dump_aws_s3_upload_frequency script

Approach
    * Load data from JSON file into Pandas dataframe ( assumes json keys are S3 objects and values are last updated timestamps)
    * Generate chart of the frequency of uploads "bucketed" in 5-min intervals (a.k.a how many files were uploaded every 5 min)
    * Save the chart as image in the local folder

<customer-name>-uploads-frequqncy.png
"""
import pandas as pd 
from datetime import datetime, timezone, timedelta

df2 = pd.read_json(
    path_or_buf='testrun-list-objects-out.json', 
    orient='values', 
    convert_dates=True, 
    typ='series'
).to_frame('last_updated')

filtered_df = df2[ df2['last_updated'] > datetime.now(tz=timezone.utc) - timedelta(hours=24) ]

plot = filtered_df.resample('5min', on='last_updated').count().plot(kind='bar')
plot.get_figure().savefig('testrun.png')    