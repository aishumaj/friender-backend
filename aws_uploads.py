import boto3

IMAGE = "/Users/margaret/dev/rithm/Sprints/friender/friender-backend/img/test-pic.jpeg"

s3 = boto3.resource('s3')
BUCKET = "rithmbucket"

s3.Bucket(BUCKET).upload_file(IMAGE, BUCKET, "test-pic.jpeg")