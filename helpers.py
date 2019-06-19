import boto3, botocore
import braintree

from config import Config 

s3 = boto3.client(
   "s3",
   aws_access_key_id=Config.S3_KEY,
   aws_secret_access_key=Config.S3_SECRET
)

gateway = braintree.BraintreeGateway(
  braintree.Configuration(
    environment=braintree.Environment.Sandbox,
    merchant_id=Config.BRAINTREE_MERCHANT_ID,
    public_key=Config.BRAINTREE_PUBLIC_KEY,
    private_key=Config.BRAINTREE_PRIVATE_KEY
  )
)