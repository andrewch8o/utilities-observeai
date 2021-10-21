<#
Extracts audio channels from stereo audio file
#>

param (
    $AudioFile
)

$inputFilePath = $AudioFile.FullName
"Processing $inputFilePath" | Write-Host
$inputFileDir = Split-Path -Path $inputFilePath -Parent
$inputFileName = Split-Path -Path $inputFilePath -Leaf
$ch0_outFilePath = Join-Path -Path $inputFileDir -ChildPath "ch0-$inputFileName"
$ch1_outFilePath = Join-Path -Path $inputFileDir -ChildPath "ch1-$inputFileName"
"Extracting channel 0" | Write-Host
ffmpeg -i $inputFilePath -af "pan=1|c0=c0" $ch0_outFilePath
"Extracting channel 1" | Write-Host
ffmpeg -i $inputFilePath -af "pan=1|c0=c1" $ch1_outFilePath