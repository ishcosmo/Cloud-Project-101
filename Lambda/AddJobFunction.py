import os, boto3, json, uuid, datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
JOBS_TABLE_NAME = os.environ.get('JOBS_TABLE_NAME')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        job_title = body.get('job_title')
        skills_str = body.get('skills', '')
        if not job_title or not skills_str: raise ValueError("job_title and skills are required")

        skills = sorted([s.strip().lower() for s in skills_str.split(',')])
        job_id = str(uuid.uuid4())
        table = dynamodb.Table(JOBS_TABLE_NAME)
        table.put_item(Item={
            'job_id': job_id, 'title': job_title, 'required_skills': skills, 
            'posted_at': datetime.datetime.utcnow().isoformat()
        })
        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=json.dumps({'job_id': job_id}))
        return { 'statusCode': 200, 'headers': { 'Access-Control-Allow-Origin': '*' }, 'body': json.dumps({'message': 'Job posted successfully!'}) }
    except Exception as e:
        return { 'statusCode': 500, 'headers': { 'Access-Control-Allow-Origin': '*' }, 'body': json.dumps({'error': str(e)}) }

