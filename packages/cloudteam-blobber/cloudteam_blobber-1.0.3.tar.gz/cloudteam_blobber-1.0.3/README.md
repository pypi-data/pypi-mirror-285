# CloudTeam_Logger

## Table of Contents

- [About](#about)
- [Usage](#usage)
- [Functions](../function.md)

## About <a name = "about"></a>

This module is a Blobber module for cloudteam to simplify the Blob operations

## Usage <a name = "usage"></a>

in you code write the following line:    
```
from cloudteam_blobber import cloudteam_blobber
BlobObj = cloudteam_blobber.blobber(<MinIO full URL>,<MinIO Access Key>,<MinIO Secret key>,<log Object>,<True or False for ssl connection>)
BlobObj.<WANTED FUNCTION>(<needed parameters>)
```

## Functions <a name = "function"></a>
- Get_Blob(bucket,filename,PathToDownload) - download the file filename from the bucker from minIO to the desired PathToDownload(Add to the path the desired file name)
- Put_Blob(bucket,file) - upload the file to the bucket
- List_Blob(optional - bucket) - if bucket specified: return all the names of the blobs in the bucket, else return all the names of the blobs in all the buckets
- List_Buckets - return all the buckets
- Blob_Metadata(bucket,blob) - return the metadata for the file in the bucket