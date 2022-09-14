import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import logging
load_dotenv()

S3_KEY = os.environ.get('S3_KEY')
S3_SECRET = os.environ.get('S3_SECRET')
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_LOCATION = os.environ.get('S3_LOCATION')

IMAGE = "img/test_pic.jpeg"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file_name, bucket, object_name, acl="public-read"):
    print("what is file name: ", file_name)
    #Upload file
    s3 = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET)
    
    try:
        with open(file_name, 'rb') as data:
            print("what is data: ", data)
            response = s3.upload_fileobj(
                data, 
                bucket, 
                object_name,
                ExtraArgs={
                    "ACL": acl,
                    "ContentType": "image/png"
            })
            print("response from s3: ", response)
    except ClientError as e:
        logging.error(e)
        return False
    return True
        
upload_file(IMAGE, S3_BUCKET,"test")

       