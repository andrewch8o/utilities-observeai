<#
Uses ffprobe to output codec information for an audio file
#>
param (
    $audioFile
)

ffprobe -hide_banner -show_streams $audioFile | grep codec