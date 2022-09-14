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


def upload_file(file_name, bucket, object_name):
    print("what is file name: ", file_name)
    #Upload file
    s3 = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET)

    try:
        response = s3.upload_fileobj(
            file_name,
            bucket,
            object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

