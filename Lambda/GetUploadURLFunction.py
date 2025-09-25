import os
import boto3
import json
import uuid

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('file_name')
        if not file_name:
            raise ValueError("file_name is a required parameter")

        object_key = f"resumes/{uuid.uuid4()}-{file_name}"

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': BUCKET_NAME, 'Key': object_key, 'ContentType': 'application/pdf'},
            ExpiresIn=3600
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({'uploadURL': presigned_url})
        }
    except Exception as e:
        return { 'statusCode': 500, 'headers': { 'Access-Control-Allow-Origin': '*' }, 'body': json.dumps({'error': str(e)}) }
