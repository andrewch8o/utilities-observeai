<#
.DESCRIPTION
    Uses AWS S3API toolset to dump latest uploaded files and converts output to CSV for further processing

    Parameters
        Bucket      - name of the S3 bucket 
            Example: observe-sftp-data-transfer

        Prefix      - S3 prefix to dump uploads for
            Example: ISPN/

        LastModieid - String representing the date stamp to dump uploads after
            Example: "2021-09-27"
#>  

param (
    $Bucket,
    $Prefix,
    $LastModified
)

aws s3api list-objects `
    --bucket $Bucket `
    --prefix $Prefix `
    --query "Contents[?LastModified > '$LastModified']" `
| set-content ./s3-uploads-dump.json

convertfrom-json ( get-content -raw ./s3-uploads-dump.json ) `
    | select LastModified,Key `
    | export-csv ./s3-uploads-dump.csv