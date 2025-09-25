import os, boto3, json

dynamodb = boto3.resource('dynamodb')
JOBS_TABLE_NAME = os.environ.get('JOBS_TABLE_NAME')
CANDIDATES_TABLE_NAME = os.environ.get('CANDIDATES_TABLE_NAME')

def lambda_handler(event, context):
    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        job_id = message.get('job_id')
        if not job_id: return
        jobs_table = dynamodb.Table(JOBS_TABLE_NAME)
        job = jobs_table.get_item(Key={'job_id': job_id}).get('Item')
        if not job: return
        required_skills = set(job.get('required_skills', []))
        candidates_table = dynamodb.Table(CANDIDATES_TABLE_NAME)
        for candidate in candidates_table.scan().get('Items', []):
            if required_skills.intersection(set(candidate.get('skills', []))):
                print(f"--- SIMULATING NOTIFICATION to {candidate.get('candidate_id')} for job {job.get('title')} ---")
    except Exception as e:
        print(f"Error in Notifier: {str(e)}")
        raise e
