"""
The script solves problem of promptly-ish visualizing frequency of file uploads under particular S3 path.

Approach:
    * Use boto3 list-objects API to pull info for all the files under S3 path ( can take long time )
    * Dump the extracted data to JSON file in the local folder
    * Load JSON file into Pandas dataframe
    * Generate chart of the frequency of uploads "bucketed" in 5-min intervals (a.k.a how many files were uploaded every 5 min)
    * Save the chart as image in the local folder

Parameters:
    --s3-path s3://<bucket>/s3/path/
        S3 path to process the files under ( recursively )
    --output-label <customer-name>
        Used to generate output files
        <customer-name>-list-objects-out.json
        <customer-name>-uploads-frequqncy.png
"""

if __name__ == '__main__':
    pass