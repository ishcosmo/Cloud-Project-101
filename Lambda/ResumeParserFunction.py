import os
import boto3
import json
import re
import datetime
from urllib.parse import unquote_plus

# Initialize clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
CANDIDATES_TABLE_NAME = os.environ.get('CANDIDATES_TABLE_NAME')

# Pre-compile regex for efficiency
EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
SKILL_LIST = {'python', 'java', 'aws', 'sql', 'javascript', 'react', 'docker', 'lambda', 's3'}

def lambda_handler(event, context):
    try:
        # 1. Get the bucket and key from the S3 event
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        print(f"INFO: Processing started for file: s3://{bucket}/{key}")

        # 2. Call Textract to detect text
        try:
            print("INFO: Attempting to process document with S3Object reference...")
            response = textract_client.detect_document_text(
                Document={'S3Object': {'Bucket': bucket, 'Name': key}}
            )
            print("INFO: Textract processing successful.")
        except Exception as e:
            print(f"ERROR: Textract failed with S3Object reference. Error: {str(e)}")
            # Re-raise the exception to stop the function and see the clear error
            raise e

        # 3. Extract text from the Textract response
        full_text = ""
        for block in response.get('Blocks', []):
            if block.get('BlockType') == 'LINE':
                full_text += block.get('Text', '') + '\n'

        if not full_text:
            print("WARNING: Textract did not detect any text in the document.")
            return

        # 4. Find email and skills
        email_match = EMAIL_RE.search(full_text)
        if not email_match:
            print(f"CRITICAL ERROR: No email address was found in the text of the document: {key}")
            return
            
        candidate_id = email_match.group(0).lower()
        words = set(re.findall(r'\b\w+\b', full_text.lower()))
        found_skills = sorted(list(SKILL_LIST.intersection(words)))
        print(f"INFO: Found candidate: {candidate_id} with skills: {found_skills}")

        # 5. Prepare item for DynamoDB (handles empty skills list)
        item_to_save = {
            'candidate_id': candidate_id,
            'resume_s3_key': key,
            'parsed_at': datetime.datetime.utcnow().isoformat()
        }
        if found_skills:
            item_to_save['skills'] = found_skills
        
        # 6. Save the result to DynamoDB
        table = dynamodb.Table(CANDIDATES_TABLE_NAME)
        table.put_item(Item=item_to_save)
        
        print(f"SUCCESS: Saved item to DynamoDB for candidate: {candidate_id}")
        return {'statusCode': 200, 'body': 'Resume parsed successfully'}

    except Exception as e:
        print(f"FATAL ERROR: An unrecoverable error occurred in the handler: {str(e)}")
        raise e
