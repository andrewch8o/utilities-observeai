<#
Creates random file of given size (in megabytes) at a given path

Example of use
gci ./IDX/ -File | % { 
    create_rand_file.ps1 -out_file_path './WAV/$($_.Name).wav' -file_size_mbytes 5 
}

A.k.a For each metadata file under ./IDX folder create 
a corresponding wav file under the ./WAV folder
#>

param(
    $out_file_path,
    $file_size_mbytes
)

dd if=/dev/urandom of=$out_file_path bs=$(1024*1024) count=$file_size_mbytes