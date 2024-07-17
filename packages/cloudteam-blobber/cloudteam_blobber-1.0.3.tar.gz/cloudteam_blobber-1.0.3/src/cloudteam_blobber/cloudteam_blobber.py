from minio import Minio
import os
from cloudteam_logger import cloudteam_logger

class blobber:
    def __init__(self,MinIODomain,MinIOAccessKey,MinIOSecretKey,LoggerObj,Secured = True):
        self.client = Minio(MinIODomain,MinIOAccessKey,MinIOSecretKey,secure=Secured)
        self.log = LoggerObj
    

    def Get_Blob(self,bucket,filename,PathToDownload):
        try:
            self.client.fget_object(bucket,filename,PathToDownload)
        except Exception as error:
            self.log.error(f'Unable to download File: {error}')
            return error
        self.log.info(f'Downloaded {filename} successfuly')
    

    def Put_Blob(self,bucket,file):
        file_name = os.path.basename(file)
        try:
            self.client.fput_object(
                bucket,
                file_name,
                file
            )
        except Exception as error:
            self.log.error(f'Unable to PUT file: {error}')
            return
        self.log.info(f'Uploaded file: {file} successfuly')

    
    def List_Blob(self,bucket = ''):
        objects = []
        if(not bucket):
            try:
                buckets = self.client.list_buckets()
            except Exception as error:
                self.log.error("Unable to list buckets: %s",error)
                return error
        else:
            buckets = [bucket]
        allBLOBs = {}
        for buck in buckets:
            try:
                try:
                    bucket = buck.name
                except:
                    bucket = buck
                objects = self.client.list_objects(bucket)
            except Exception as error:
                self.log.error(f'Unable to list objects of in bucket: {error}')
                return error
            blobsNames  = []
            try:
                for obj in objects:
                    blobsNames.append(obj.object_name)
                allBLOBs[bucket] = blobsNames
            except:
                self.log.error("Unable to unable to connect to bucket or there is no buckets")
                return error
        return allBLOBs
    

    def List_Buckets(self):
        try:
            buckets = self.client.list_buckets()
        except Exception as error:
            self.log.error("Unable to list buckets: %s",error)
            return error
        bucket_list= []
        for bucket in buckets:
            bucket_list.append(bucket.name)
        return bucket_list
    

    def Blob_Metadata(self,bucket,blob):
        try:
            metadata = self.client.stat_object(bucket,blob)
        except Exception as error:
            self.log.error("Unable to return blob metadata: %s",error)
            return error
        return metadata
