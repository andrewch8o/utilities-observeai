<#
.DESCRIPTION
    Produces list of files uploaded to S3 location after the specified date
#>
param (
    $Bucket,
    $Prefix,
    $MetaSuffix,
    $LastModified
)

$s3query = "Contents[?ends_with(Key, '$MetaSuffix') && LastModified > '$LastModified']"

"Running S3 query: '$s3query' (bucket: '$($Bucket)', prefix: '$($Prefix)')" | Out-Host
$resp_raw = (aws s3api list-objects --bucket $Bucket --prefix $Prefix --query $s3query) | Out-String -NoNewline
$resp = ConvertFrom-Json -InputObject $resp_raw

return ( $resp | % { "s3://$Bucket/$($_.Key)" } )
