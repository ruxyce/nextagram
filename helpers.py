import boto3, botocore
from config import Config 

from flask import render_template, request, redirect, url_for

from models.post import Post, AvatarKey

import random
import string

s3 = boto3.client(
   "s3",
   aws_access_key_id=Config.S3_KEY,
   aws_secret_access_key=Config.S3_SECRET
)

# added prepend_string


    

def upload_image_s3(file, bucket_name, prepend_string='', acl="public-read"):

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            prepend_string+file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(Config.S3_LOCATION, prepend_string+file.filename)



# ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))