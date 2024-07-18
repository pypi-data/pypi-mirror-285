import os
import io
import boto3
from pathlib import Path
from botocore.exceptions import ClientError
# from . import aws_helper

AWS_REGION='us-east-1'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
# def getInfoBykey(bucket, key):
#     """获取s3文件对象的信息（用于调试）

#     Args:
#         bucket (_type_): _description_
#         key (_type_): _description_
#     """
#     s3Res = aws_helper.getS3Resource() 
#     obj = s3Res.Object(bucket, key)
#     bytes = obj.get()['Body'].read()
    
def uploadFile_bytes(bucket, key, bytes, s3_client=None):
    """写入文件"""
    if not s3_client:
        s3_client = boto3.client("s3", region_name=AWS_REGION)
    with io.BytesIO() as f:
        f.write(bytes)
        f.seek(0)
        s3_client.upload_fileobj(f,bucket,key)
        
def uploadFile(bucket, key, file:str):
    """写入文件"""
    with io.BytesIO() as f:
        f.write(bytes)
        f.seek(0)
        s3_client = boto3.client("s3", region_name=AWS_REGION)
        s3_client.upload_file(f,bucket,key)
        
def downloadToLocal(bucket, key, saveFileToPath):
    """下载文件到本地"""
    s3_resource = boto3.resource("s3", region_name=AWS_REGION)
    s3_object = s3_resource.Object(bucket, key)
    Path(saveFileToPath).parent.mkdir(exist_ok=True)
    s3_object.download_file(saveFileToPath)
    
def download_dir(prefix, local, bucket, client=s3_client):
    """
    params:
    - prefix: pattern to match in s3
    - local: local path to folder in which to place files
    - bucket: s3 bucket with target contents
    - client: initialized s3 client object
    """
    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket':bucket,
        'Prefix':prefix,
    }
    # print("mark 1")
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        results = client.list_objects_v2(**kwargs)
        contents = results.get('Contents')
        for i in contents:
            k = i.get('Key')
            if k[-1] != '/':
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get('NextContinuationToken')
    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
    for k in keys:
        dest_pathname = os.path.join(local, k)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        client.download_file(bucket, k, dest_pathname)

def upload_dir(dir, bucket, prefix='', session=None):
    if not session:
        session = boto3.Session()
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket)
 
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, 'rb') as data:
                key = prefix + full_path[len(dir)+1:]
                print(f"key={key}")
                bucket.put_object(Key=key, Body=data)
    
def copy_to_other_bucket(src, des, key):
    try:
        copy_source = {
            'Bucket': src,
            'Key': key
        }
        bucket = s3.Bucket(des)
        bucket.copy(copy_source, key)
    except Exception as e:
        print(e)
    
def delete(bucket, key):    
    s3_client = boto3.client("s3", region_name=AWS_REGION)    
    s3_client.delete_object(Bucket=bucket, Key=key)
    
# To check whether root bucket exists or not
def bucket_exists(bucket_name):
   try:
      session = boto3.session.Session()
      # User can pass customized access key, secret_key and token as well
      s3_client = session.client('s3')
      s3_client.head_bucket(Bucket=bucket_name)
      print("Bucket exists.", bucket_name)
      exists = True
   except ClientError as error:
      error_code = int(error.response['Error']['Code'])
      if error_code == 403:
         print("Private Bucket. Forbidden Access! ", bucket_name)
      elif error_code == 404:
        #  print("Bucket Does Not Exist!", bucket_name)
        pass
      exists = False
   return exists